from django.contrib import admin
from .models import Course, Exam, Question, Submission, Answer


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'created_at']
    search_fields = ['code', 'name']
    ordering = ['code']


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ['order', 'question_text', 'question_type', 'marks', 'expected_answer']


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'status', 'duration_minutes', 'total_marks', 'start_time', 'created_at']
    list_filter = ['status', 'course', 'created_at']
    search_fields = ['title', 'course__name']
    inlines = [QuestionInline]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('course', 'title', 'description', 'status')
        }),
        ('Exam Settings', {
            'fields': ('duration_minutes', 'total_marks', 'passing_score')
        }),
        ('Schedule', {
            'fields': ('start_time', 'end_time')
        }),
        ('Metadata', {
            'fields': ('created_by',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['exam', 'question_type', 'order', 'marks', 'question_text_short']
    list_filter = ['question_type', 'exam']
    search_fields = ['question_text', 'exam__title']
    ordering = ['exam', 'order']
    
    def question_text_short(self, obj):
        return obj.question_text[:100] + '...' if len(obj.question_text) > 100 else obj.question_text
    question_text_short.short_description = 'Question'


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    fields = ['question', 'answer_text', 'score', 'feedback']
    readonly_fields = ['question', 'answer_text', 'score', 'feedback']


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam', 'status', 'score', 'percentage', 'submitted_at', 'graded_at']
    list_filter = ['status', 'exam', 'submitted_at']
    search_fields = ['student__username', 'exam__title']
    readonly_fields = ['started_at', 'submitted_at', 'graded_at', 'grading_metadata']
    inlines = [AnswerInline]
    date_hierarchy = 'submitted_at'
    
    fieldsets = (
        ('Submission Info', {
            'fields': ('student', 'exam', 'status')
        }),
        ('Grading', {
            'fields': ('score', 'percentage', 'feedback')
        }),
        ('Timestamps', {
            'fields': ('started_at', 'submitted_at', 'graded_at')
        }),
        ('Metadata', {
            'fields': ('grading_metadata',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['submission', 'question', 'score', 'created_at']
    list_filter = ['submission__exam', 'created_at']
    search_fields = ['submission__student__username', 'question__question_text']
    readonly_fields = ['created_at', 'updated_at']