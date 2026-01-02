from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.utils import timezone
from django.db import transaction
from django.db.models import Prefetch, Q, Count, Avg
from .models import Course, Exam, Question, Submission, Answer
from .serializers import (
    CourseSerializer, ExamListSerializer, ExamDetailSerializer,
    QuestionSerializer, SubmissionCreateSerializer, SubmissionListSerializer,
    SubmissionDetailSerializer, UserSerializer
)
from .grading_service import GradingService


class IsOwnerOrAdmin(permissions.BasePermission):
    """Custom permission to only allow owners or admins"""
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        
        if isinstance(obj, Submission):
            return obj.student == request.user
        
        return False


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for viewing courses"""
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Course.objects.annotate(exam_count=Count('exams'))


class ExamViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for viewing exams"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Exam.objects.select_related('course', 'created_by')
        
        if not self.request.user.is_staff:
            queryset = queryset.filter(status='published')
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ExamDetailSerializer
        return ExamListSerializer
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if not request.user.is_staff and not instance.is_active():
            raise PermissionDenied("This exam is not currently available")
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        exam = self.get_object()
        
        if not exam.is_active():
            return Response(
                {'error': 'This exam is not currently available'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        existing = Submission.objects.filter(
            student=request.user,
            exam=exam
        ).first()
        
        if existing:
            return Response(
                {'error': 'You have already started this exam',
                 'submission_id': existing.id},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        submission = Submission.objects.create(
            student=request.user,
            exam=exam,
            status='in_progress'
        )
        
        return Response({
            'submission_id': submission.id,
            'started_at': submission.started_at,
            'exam': ExamDetailSerializer(exam).data
        }, status=status.HTTP_201_CREATED)


class SubmissionViewSet(viewsets.ModelViewSet):
    """API endpoint for managing exam submissions"""
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    
    def get_queryset(self):
        queryset = Submission.objects.select_related(
            'student', 'exam', 'exam__course'
        ).prefetch_related(
            Prefetch('answers', queryset=Answer.objects.select_related('question'))
        )
        
        if not self.request.user.is_staff:
            queryset = queryset.filter(student=self.request.user)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action in ['retrieve', 'grade']:
            return SubmissionDetailSerializer
        elif self.action == 'submit':
            return SubmissionCreateSerializer
        return SubmissionListSerializer
    
    @transaction.atomic
    @action(detail=False, methods=['post'])
    def submit(self, request):
        serializer = SubmissionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        exam_id = serializer.validated_data['exam_id']
        answers_data = serializer.validated_data['answers']
        
        exam = Exam.objects.select_related('course').get(id=exam_id)
        
        submission, created = Submission.objects.get_or_create(
            student=request.user,
            exam=exam,
            defaults={'status': 'in_progress'}
        )
        
        if submission.status == 'submitted' or submission.status == 'graded':
            return Response(
                {'error': 'This exam has already been submitted'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        for answer_data in answers_data:
            question = Question.objects.get(id=answer_data['question_id'])
            Answer.objects.update_or_create(
                submission=submission,
                question=question,
                defaults={'answer_text': answer_data['answer_text']}
            )
        
        submission.status = 'submitted'
        submission.submitted_at = timezone.now()
        submission.save()
        
        self._grade_submission(submission)
        
        submission.refresh_from_db()
        
        return Response(
            SubmissionDetailSerializer(submission).data,
            status=status.HTTP_201_CREATED
        )
    
    def _grade_submission(self, submission):
        grading_service = GradingService()
        
        answers = submission.answers.select_related('question').all()
        
        grading_data = []
        for answer in answers:
            grading_data.append({
                'question_id': answer.question.id,
                'question_type': answer.question.question_type,
                'student_answer': answer.answer_text,
                'expected_answer': answer.question.expected_answer,
                'max_marks': answer.question.marks,
                'rubric': answer.question.grading_rubric
            })
        
        result = grading_service.grade_submission(grading_data)
        
        submission.score = result['total_score']
        submission.percentage = result['percentage']
        submission.status = 'graded'
        submission.graded_at = timezone.now()
        submission.grading_metadata = {
            'grading_method': 'automated',
            'graded_at': submission.graded_at.isoformat()
        }
        submission.calculate_percentage()
        
        if submission.is_passed():
            submission.feedback = f"Congratulations! You passed with {submission.percentage}%"
        else:
            submission.feedback = f"You scored {submission.percentage}%. Passing score is {submission.exam.passing_score}%"
        
        submission.save()
        
        for detail in result['detailed_results']:
            answer = answers.get(question_id=detail['question_id'])
            answer.score = detail['score']
            answer.feedback = detail['feedback']
            answer.grading_details = detail['grading_details']
            answer.save()
    
    @action(detail=True, methods=['post'])
    def regrade(self, request, pk=None):
        if not request.user.is_staff:
            raise PermissionDenied("Only staff can regrade submissions")
        
        submission = self.get_object()
        
        if submission.status not in ['submitted', 'graded']:
            return Response(
                {'error': 'Can only regrade submitted submissions'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        self._grade_submission(submission)
        submission.refresh_from_db()
        
        return Response(SubmissionDetailSerializer(submission).data)
    
    @action(detail=False, methods=['get'])
    def my_results(self, request):
        submissions = self.get_queryset().filter(
            status='graded'
        ).order_by('-submitted_at')
        
        total_exams = submissions.count()
        passed_exams = sum(1 for s in submissions if s.is_passed())
        
        avg_score = submissions.aggregate(avg=Avg('percentage'))['avg'] or 0
        
        stats = {
            'total_exams': total_exams,
            'passed_exams': passed_exams,
            'failed_exams': total_exams - passed_exams,
            'average_percentage': round(avg_score, 2),
            'pass_rate': round((passed_exams / total_exams * 100), 2) if total_exams > 0 else 0
        }
        
        serializer = SubmissionListSerializer(submissions, many=True)
        
        return Response({
            'statistics': stats,
            'submissions': serializer.data
        })


class UserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for user profile"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return [self.request.user]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)