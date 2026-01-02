from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Course(models.Model):
    """Represents an academic course"""
    code = models.CharField(max_length=20, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['code']
        indexes = [
            models.Index(fields=['code']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Exam(models.Model):
    """Represents an exam/assessment"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='exams')
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Duration in minutes"
    )
    passing_score = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=60.00
    )
    total_marks = models.PositiveIntegerField(default=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_exams')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'start_time']),
            models.Index(fields=['course', 'status']),
        ]
    
    def is_active(self):
        """Check if exam is currently active"""
        now = timezone.now()
        if self.status != 'published':
            return False
        if self.start_time and now < self.start_time:
            return False
        if self.end_time and now > self.end_time:
            return False
        return True
    
    def __str__(self):
        return f"{self.course.code} - {self.title}"


class Question(models.Model):
    """Represents a question in an exam"""
    QUESTION_TYPES = [
        ('mcq', 'Multiple Choice'),
        ('short_answer', 'Short Answer'),
        ('essay', 'Essay'),
        ('true_false', 'True/False'),
    ]
    
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    marks = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    order = models.PositiveIntegerField(default=0)
    
    # For MCQ questions
    options = models.JSONField(
        null=True, 
        blank=True,
        help_text="JSON array of options for MCQ questions"
    )
    
    # Expected answer/solution
    expected_answer = models.TextField(
        help_text="Expected answer or keywords for grading"
    )
    
    # Grading hints for automated grading
    grading_rubric = models.JSONField(
        null=True,
        blank=True,
        help_text="Additional grading criteria as JSON"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['exam', 'order']
        indexes = [
            models.Index(fields=['exam', 'order']),
        ]
    
    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}"


class Submission(models.Model):
    """Represents a student's exam submission"""
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('submitted', 'Submitted'),
        ('graded', 'Graded'),
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='submissions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    feedback = models.TextField(blank=True)
    grading_metadata = models.JSONField(
        null=True,
        blank=True,
        help_text="Additional grading details"
    )
    
    class Meta:
        ordering = ['-submitted_at']
        unique_together = [['student', 'exam']]
        indexes = [
            models.Index(fields=['student', 'exam']),
            models.Index(fields=['status', 'submitted_at']),
            models.Index(fields=['exam', 'status']),
        ]
    
    def calculate_percentage(self):
        """Calculate percentage score"""
        if self.score is not None and self.exam.total_marks > 0:
            self.percentage = (self.score / self.exam.total_marks) * 100
    
    def is_passed(self):
        """Check if student passed the exam"""
        if self.percentage is not None:
            return self.percentage >= self.exam.passing_score
        return False
    
    def __str__(self):
        return f"{self.student.username} - {self.exam.title}"


class Answer(models.Model):
    """Represents an answer to a specific question"""
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.TextField()
    
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    
    feedback = models.TextField(blank=True)
    grading_details = models.JSONField(
        null=True,
        blank=True,
        help_text="Detailed grading breakdown"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['submission', 'question']]
        indexes = [
            models.Index(fields=['submission', 'question']),
        ]
    
    def __str__(self):
        return f"Answer to {self.question.id} by {self.submission.student.username}"