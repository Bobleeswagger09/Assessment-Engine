from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Course, Exam, Question, Submission, Answer
from django.utils import timezone


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'code', 'name', 'description', 'created_at']


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            'id', 'question_text', 'question_type', 'marks', 
            'order', 'options'
        ]


class QuestionDetailSerializer(serializers.ModelSerializer):
    """Admin view with grading details"""
    class Meta:
        model = Question
        fields = '__all__'


class ExamListSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    question_count = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()
    
    class Meta:
        model = Exam
        fields = [
            'id', 'course', 'title', 'description', 'duration_minutes',
            'total_marks', 'passing_score', 'status', 'start_time', 
            'end_time', 'is_active', 'question_count', 'created_at'
        ]
    
    def get_question_count(self, obj):
        return obj.questions.count()
    
    def get_is_active(self, obj):
        return obj.is_active()


class ExamDetailSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    questions = QuestionSerializer(many=True, read_only=True)
    is_active = serializers.SerializerMethodField()
    
    class Meta:
        model = Exam
        fields = [
            'id', 'course', 'title', 'description', 'duration_minutes',
            'total_marks', 'passing_score', 'status', 'start_time',
            'end_time', 'is_active', 'questions', 'created_at'
        ]
    
    def get_is_active(self, obj):
        return obj.is_active()


class AnswerSubmitSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    answer_text = serializers.CharField(allow_blank=True)
    
    def validate_question_id(self, value):
        if not Question.objects.filter(id=value).exists():
            raise serializers.ValidationError("Invalid question ID")
        return value


class SubmissionCreateSerializer(serializers.Serializer):
    exam_id = serializers.IntegerField()
    answers = AnswerSubmitSerializer(many=True)
    
    def validate_exam_id(self, value):
        try:
            exam = Exam.objects.get(id=value)
        except Exam.DoesNotExist:
            raise serializers.ValidationError("Invalid exam ID")
        
        if not exam.is_active():
            raise serializers.ValidationError("This exam is not currently active")
        
        return value
    
    def validate_answers(self, value):
        if not value:
            raise serializers.ValidationError("At least one answer is required")
        
        question_ids = [ans['question_id'] for ans in value]
        if len(question_ids) != len(set(question_ids)):
            raise serializers.ValidationError("Duplicate question IDs found")
        
        return value
    
    def validate(self, data):
        exam_id = data['exam_id']
        question_ids = [ans['question_id'] for ans in data['answers']]
        
        exam_questions = Question.objects.filter(
            exam_id=exam_id,
            id__in=question_ids
        ).count()
        
        if exam_questions != len(question_ids):
            raise serializers.ValidationError(
                "Some questions do not belong to this exam"
            )
        
        return data


class AnswerSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(read_only=True)
    
    class Meta:
        model = Answer
        fields = [
            'id', 'question', 'answer_text', 'score', 
            'feedback', 'grading_details', 'created_at'
        ]


class SubmissionListSerializer(serializers.ModelSerializer):
    exam = ExamListSerializer(read_only=True)
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    student_username = serializers.CharField(source='student.username', read_only=True)
    is_passed = serializers.SerializerMethodField()
    
    class Meta:
        model = Submission
        fields = [
            'id', 'exam', 'student_name', 'student_username', 'status',
            'started_at', 'submitted_at', 'graded_at', 'score',
            'percentage', 'is_passed'
        ]
    
    def get_is_passed(self, obj):
        return obj.is_passed()


class SubmissionDetailSerializer(serializers.ModelSerializer):
    exam = ExamDetailSerializer(read_only=True)
    answers = AnswerSerializer(many=True, read_only=True)
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    student_username = serializers.CharField(source='student.username', read_only=True)
    is_passed = serializers.SerializerMethodField()
    
    class Meta:
        model = Submission
        fields = [
            'id', 'exam', 'student_name', 'student_username', 'status',
            'started_at', 'submitted_at', 'graded_at', 'score',
            'percentage', 'feedback', 'grading_metadata', 'answers',
            'is_passed'
        ]
    
    def get_is_passed(self, obj):
        return obj.is_passed()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']