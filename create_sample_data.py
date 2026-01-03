import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from assessment.models import Course, Exam, Question
from django.utils import timezone
from datetime import timedelta

print("Creating sample data...")

# Create test student
student, created = User.objects.get_or_create(
    username='testuser',
    defaults={
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'User'
    }
)
if created:
    student.set_password('testpass123')
    student.save()
    print(f"✓ Created student: {student.username}")
else:
    # Reset password if user exists
    student.set_password('testpass123')
    student.save()
    print(f"✓ Student exists (password reset): {student.username}")

# Create admin if doesn't exist
admin, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@example.com',
        'is_staff': True,
        'is_superuser': True
    }
)
if created:
    admin.set_password('admin123')
    admin.save()
    print(f"✓ Created admin: {admin.username}")
else:
    admin.set_password('admin123')
    admin.save()
    print(f"✓ Admin exists (password reset): {admin.username}")

# Create course
course, created = Course.objects.get_or_create(
    code='CS101',
    defaults={
        'name': 'Introduction to Computer Science',
        'description': 'Basic programming concepts and principles'
    }
)
print(f"✓ Created course: {course.code}" if created else f"✓ Course exists: {course.code}")

# Create exam
exam, created = Exam.objects.get_or_create(
    title='Midterm Exam - OOP Fundamentals',
    course=course,
    defaults={
        'description': 'Test your knowledge of Object Oriented Programming',
        'duration_minutes': 60,
        'total_marks': 35,
        'passing_score': 60.0,
        'status': 'published',
        'start_time': timezone.now() - timedelta(hours=1),
        'end_time': timezone.now() + timedelta(days=7),
        'created_by': admin
    }
)
print(f"✓ Created exam: {exam.title}" if created else f"✓ Exam exists: {exam.title}")

# Create questions
questions_data = [
    {
        'question_text': 'What is polymorphism in Object Oriented Programming? Explain with examples.',
        'question_type': 'essay',
        'marks': 20,
        'order': 1,
        'expected_answer': 'Polymorphism is the ability of objects to take multiple forms. It allows methods to do different things based on the object type. For example, a shape class can have a draw method, and circle and square subclasses can implement it differently.',
    },
    {
        'question_text': 'What does OOP stand for?',
        'question_type': 'short_answer',
        'marks': 10,
        'order': 2,
        'expected_answer': 'Object Oriented Programming',
    },
    {
        'question_text': 'Python is a compiled language.',
        'question_type': 'true_false',
        'marks': 5,
        'order': 3,
        'expected_answer': 'false',
        'options': ['true', 'false']
    },
]

for q_data in questions_data:
    question, created = Question.objects.get_or_create(
        exam=exam,
        order=q_data['order'],
        defaults=q_data
    )
    if created:
        print(f"✓ Created question {q_data['order']}: {q_data['question_text'][:50]}...")

print("\n" + "="*60)
print("✅ Sample data created successfully!")
print("="*60)
print(f"\nLogin Credentials:")
print(f"  Admin:")
print(f"    Username: admin")
print(f"    Password: admin123")
print(f"\n  Student:")
print(f"    Username: testuser")
print(f"    Password: testpass123")
print("\nNext steps:")
print(f"  1. Get token: curl -X POST http://127.0.0.1:8080/api/auth/token/ -H 'Content-Type: application/json' -d '{{\"username\": \"testuser\", \"password\": \"testpass123\"}}'")
print(f"  2. Test API: curl http://127.0.0.1:8080/api/exams/ -H 'Authorization: Token YOUR_TOKEN'")
print("="*60)