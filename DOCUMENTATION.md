# Mini Assessment Engine - Complete Documentation

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Technology Stack](#technology-stack)
4. [Installation Guide](#installation-guide)
5. [API Documentation](#api-documentation)
6. [Security Features](#security-features)
7. [Grading System](#grading-system)
8. [Testing Guide](#testing-guide)
9. [Deployment](#deployment)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Project Overview

**Mini Assessment Engine** is a Django REST API backend system designed for Acad AI that enables students to take exams, submit answers securely, and receive automated grading feedback in real-time.

### Key Capabilities

- **Secure Authentication**: Token-based authentication with Django REST Framework
- **Exam Management**: Create and manage courses, exams, and questions
- **Automated Grading**: Three built-in grading algorithms (keyword matching, TF-IDF cosine similarity, MCQ matching)
- **Student Privacy**: Students can only view and submit their own work
- **Performance Optimized**: Query optimization with `select_related()` and `prefetch_related()`
- **API Documentation**: Auto-generated Swagger/OpenAPI documentation

---

## ✨ Features

### 1. Database Modeling ✅

- **5 Core Models**: Course, Exam, Question, Submission, Answer
- **Proper Relationships**: Foreign keys with CASCADE/SET_NULL behaviors
- **Strategic Indexing**: On frequently queried fields
- **Full Normalization**: Follows 3NF principles

### 2. Secure Submission Endpoint ✅

- **Token Authentication**: Industry-standard DRF authentication
- **Object-Level Permissions**: Students access only their own data
- **Input Validation**: Comprehensive validation at serializer level
- **CSRF Protection**: Built-in Django security

### 3. Automated Grading Logic ✅

Three grading algorithms implemented from scratch:

1. **Keyword Matching Grader** (Short Answers)

   - Extracts keywords from expected answer
   - Checks presence in student answer
   - Applies length penalties

2. **TF-IDF Cosine Similarity Grader** (Essays)

   - Computes document vectors
   - Calculates semantic similarity
   - Uses square root curve for fair scoring

3. **Exact Matching Grader** (MCQ/True-False)
   - Fast, deterministic scoring
   - Case-insensitive matching

### 4. API Documentation ✅

- **Swagger UI**: Interactive API documentation
- **Request/Response Examples**: All endpoints documented
- **Authentication Guide**: Clear token usage instructions

---

## 🛠 Technology Stack

- **Framework**: Django 4.2.7
- **API**: Django REST Framework 3.14.0
- **Database**: SQLite (development) / PostgreSQL (production recommended)
- **Authentication**: Token Authentication (DRF)
- **Documentation**: drf-spectacular 0.27.0
- **CORS**: django-cors-headers 4.3.0

---

## 📦 Installation Guide

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git (optional)

### Step 1: Clone or Download Project

```bash
# If using Git
git clone <repository-url>
cd assessment_engine

# Or download and extract ZIP file
cd assessment_engine
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**requirements.txt:**

```txt
Django==4.2.7
djangorestframework==3.14.0
drf-spectacular==0.27.0
django-cors-headers==4.3.0
```

### Step 4: Configure Database

The project uses SQLite by default (no setup needed). For PostgreSQL:

```python
# In config/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'assessment_db',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Step 5: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Create Sample Data

```bash
python create_sample_data.py
```

**Output:**

```
Creating sample data...
✓ Created student: testuser
✓ Created admin: admin
✓ Created course: CS101
✓ Created exam: Midterm Exam - OOP Fundamentals
✓ Created question 1: What is polymorphism...
✓ Created question 2: What does OOP stand for?
✓ Created question 3: Python is a compiled language.

============================================================
✅ Sample data created successfully!
============================================================

Login Credentials:
  Admin:
    Username: admin
    Password: admin123

  Student:
    Username: testuser
    Password: testpass123
```

### Step 7: Run Development Server

```bash
python manage.py runserver 8080
```

Visit: **http://127.0.0.1:8080/swagger/**

---

## 📚 API Documentation

### Base URL

```
http://127.0.0.1:8080/api/
```

### Authentication

All endpoints (except `/auth/token/`) require authentication.

**Header Format:**

```
Authorization: Token your-token-here
```

---

### Endpoints

#### 1. Authentication

**POST `/api/auth/token/`** - Get Authentication Token

**Request:**

```json
{
  "username": "testuser",
  "password": "testpass123"
}
```

**Response:**

```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user_id": 2,
  "username": "testuser",
  "email": "test@example.com"
}
```

**cURL Example:**

```bash
curl -X POST http://127.0.0.1:8080/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'
```

---

#### 2. Courses

**GET `/api/courses/`** - List All Courses

**Response:**

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "code": "CS101",
      "name": "Introduction to Computer Science",
      "description": "Basic programming concepts",
      "created_at": "2026-01-03T10:00:00Z"
    }
  ]
}
```

**cURL Example:**

```bash
curl http://127.0.0.1:8080/api/courses/ \
  -H "Authorization: Token YOUR_TOKEN"
```

---

#### 3. Exams

**GET `/api/exams/`** - List Available Exams

**Response:**

```json
{
  "count": 1,
  "results": [
    {
      "id": 1,
      "course": {
        "id": 1,
        "code": "CS101",
        "name": "Introduction to Computer Science"
      },
      "title": "Midterm Exam - OOP Fundamentals",
      "description": "Test your knowledge of OOP",
      "duration_minutes": 60,
      "total_marks": 35,
      "passing_score": 60.0,
      "status": "published",
      "is_active": true,
      "question_count": 3,
      "start_time": "2026-01-03T09:00:00Z",
      "end_time": "2026-01-10T09:00:00Z"
    }
  ]
}
```

**GET `/api/exams/{id}/`** - Get Exam with Questions

**Response:**

```json
{
  "id": 1,
  "course": {...},
  "title": "Midterm Exam - OOP Fundamentals",
  "questions": [
    {
      "id": 1,
      "question_text": "What is polymorphism in OOP?",
      "question_type": "essay",
      "marks": 20,
      "order": 1
    },
    {
      "id": 2,
      "question_text": "What does OOP stand for?",
      "question_type": "short_answer",
      "marks": 10,
      "order": 2
    },
    {
      "id": 3,
      "question_text": "Python is a compiled language.",
      "question_type": "true_false",
      "marks": 5,
      "order": 3,
      "options": ["true", "false"]
    }
  ]
}
```

**POST `/api/exams/{id}/start/`** - Start an Exam

Creates a submission record for tracking.

**Response:**

```json
{
  "submission_id": 1,
  "started_at": "2026-01-03T10:30:00Z",
  "exam": {...}
}
```

---

#### 4. Submissions

**POST `/api/submissions/submit/`** - Submit Exam Answers

**Request:**

```json
{
  "exam_id": 1,
  "answers": [
    {
      "question_id": 1,
      "answer_text": "Polymorphism is the ability of objects to take multiple forms. It allows methods to do different things based on the object type."
    },
    {
      "question_id": 2,
      "answer_text": "Object Oriented Programming"
    },
    {
      "question_id": 3,
      "answer_text": "false"
    }
  ]
}
```

**Response (Auto-Graded):**

```json
{
  "id": 1,
  "exam": {...},
  "student_name": "Test User",
  "student_username": "testuser",
  "status": "graded",
  "started_at": "2026-01-03T10:30:00Z",
  "submitted_at": "2026-01-03T10:45:00Z",
  "graded_at": "2026-01-03T10:45:02Z",
  "score": 28.5,
  "percentage": 81.43,
  "is_passed": true,
  "feedback": "Congratulations! You passed with 81.43%",
  "answers": [
    {
      "id": 1,
      "question": {...},
      "answer_text": "Polymorphism is...",
      "score": 18.5,
      "feedback": "Good coverage of key concepts: polymorphism, objects, forms",
      "grading_details": {
        "strategy": "cosine_similarity",
        "similarity_score": 0.85
      }
    },
    {
      "id": 2,
      "question": {...},
      "answer_text": "Object Oriented Programming",
      "score": 10.0,
      "feedback": "Good coverage of key concepts",
      "grading_details": {
        "strategy": "keyword_matching",
        "match_percentage": 100.0
      }
    },
    {
      "id": 3,
      "question": {...},
      "answer_text": "false",
      "score": 5.0,
      "feedback": "Correct!",
      "grading_details": {
        "strategy": "mcq",
        "is_correct": true
      }
    }
  ]
}
```

**cURL Example:**

```bash
curl -X POST http://127.0.0.1:8080/api/submissions/submit/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "exam_id": 1,
    "answers": [
      {"question_id": 1, "answer_text": "Polymorphism allows objects to take multiple forms"},
      {"question_id": 2, "answer_text": "Object Oriented Programming"},
      {"question_id": 3, "answer_text": "false"}
    ]
  }'
```

**GET `/api/submissions/`** - List Your Submissions

Only shows submissions belonging to the authenticated user.

**GET `/api/submissions/{id}/`** - Get Submission Details

Only accessible if you own the submission or are an admin.

**GET `/api/submissions/my_results/`** - Get Results with Statistics

**Response:**

```json
{
  "statistics": {
    "total_exams": 5,
    "passed_exams": 4,
    "failed_exams": 1,
    "average_percentage": 78.5,
    "pass_rate": 80.0
  },
  "submissions": [...]
}
```

**POST `/api/submissions/{id}/regrade/`** - Regrade Submission (Admin Only)

---

#### 5. User Profile

**GET `/api/users/me/`** - Get Current User Profile

**Response:**

```json
{
  "id": 2,
  "username": "testuser",
  "email": "test@example.com",
  "first_name": "Test",
  "last_name": "User"
}
```

---

## 🔒 Security Features

### 1. Authentication & Authorization

- **Token Authentication**: Secure, stateless authentication
- **Permission Classes**: `IsAuthenticated`, `IsOwnerOrAdmin`
- **Session Security**: HttpOnly cookies, CSRF protection

### 2. Submission Ownership Enforcement

**Critical Security Feature:**

```python
class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if isinstance(obj, Submission):
            return obj.student == request.user  # Ownership check
        return False
```

**QuerySet Filtering:**

```python
def get_queryset(self):
    queryset = Submission.objects.select_related(...)
    if not self.request.user.is_staff:
        queryset = queryset.filter(student=self.request.user)
    return queryset
```

**What This Means:**

- ✅ Students can ONLY submit their own work
- ✅ Students can ONLY view their own submissions
- ✅ Students CANNOT access other students' data
- ✅ Admins have full access

### 3. Input Validation

- Serializer-level validation
- Foreign key validation
- Duplicate submission prevention
- Exam availability checks

### 4. Database Security

- SQL injection protection via Django ORM
- Parameterized queries
- No raw SQL execution

### 5. Rate Limiting

```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}
```

---

## 🎓 Grading System

### Architecture

The grading system uses a **Strategy Pattern** for modularity:

```python
class GradingStrategy(ABC):
    @abstractmethod
    def grade(self, student_answer, expected_answer, max_marks, rubric):
        pass

class GradingService:
    def __init__(self):
        self.strategies = {
            'mcq': MCQGrader(),
            'true_false': MCQGrader(),
            'short_answer': KeywordMatchingGrader(),
            'essay': CosineSimilarityGrader(),
        }
```

### Algorithm 1: Keyword Matching

**Use Case**: Short answer questions, definitions

**How It Works:**

1. Extract keywords from expected answer (remove stop words)
2. Check for presence in student answer
3. Calculate match percentage
4. Apply length penalty for very short answers
5. Generate specific feedback

**Example:**

```
Expected: "Object Oriented Programming focuses on objects and classes"
Student: "OOP uses objects and classes"
Match: ["objects", "classes"] = 66.67%
Score: 6.67 / 10
```

### Algorithm 2: TF-IDF Cosine Similarity

**Use Case**: Essay questions, explanations

**How It Works:**

1. Tokenize both answers
2. Compute TF-IDF vectors for each
3. Calculate cosine similarity
4. Apply square root curve for fair scoring
5. Generate feedback based on similarity level

**Example:**

```
Expected: "Polymorphism allows objects to take multiple forms..."
Student: "Polymorphism enables objects to have different forms..."
Similarity: 0.85
Adjusted: √0.85 = 0.92
Score: 18.4 / 20
```

### Algorithm 3: Exact Matching

**Use Case**: MCQ, True/False questions

**How It Works:**

1. Normalize answers (lowercase, trim)
2. Compare for exact match
3. Return full marks or zero

**Example:**

```
Expected: "false"
Student: "False"
Normalized Match: true
Score: 5 / 5
```

### Extending with LLM

The system is designed for easy LLM integration:

```python
class LLMGrader(GradingStrategy):
    def grade(self, student_answer, expected_answer, max_marks, rubric):
        # Call OpenAI/Anthropic/etc.
        prompt = f"Grade this answer: {student_answer}"
        response = llm_api.complete(prompt)
        return score, feedback, details

# Register new grader
grading_service.strategies['essay'] = LLMGrader()
```

---

## 🧪 Testing Guide

### Manual Testing with cURL

**Complete Test Flow:**

```bash
# 1. Get token
TOKEN=$(curl -s -X POST http://127.0.0.1:8080/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}' \
  | grep -o '"token":"[^"]*' | cut -d'"' -f4)

echo "Token: $TOKEN"

# 2. List courses
curl http://127.0.0.1:8080/api/courses/ \
  -H "Authorization: Token $TOKEN"

# 3. List exams
curl http://127.0.0.1:8080/api/exams/ \
  -H "Authorization: Token $TOKEN"

# 4. Get exam details
curl http://127.0.0.1:8080/api/exams/1/ \
  -H "Authorization: Token $TOKEN"

# 5. Submit exam
curl -X POST http://127.0.0.1:8080/api/submissions/submit/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "exam_id": 1,
    "answers": [
      {"question_id": 1, "answer_text": "Polymorphism allows objects to take multiple forms"},
      {"question_id": 2, "answer_text": "Object Oriented Programming"},
      {"question_id": 3, "answer_text": "false"}
    ]
  }'

# 6. View results
curl http://127.0.0.1:8080/api/submissions/my_results/ \
  -H "Authorization: Token $TOKEN"
```

### Testing with Postman

1. Import the API into Postman
2. Create environment variable: `base_url = http://127.0.0.1:8080/api`
3. Get token and save as `auth_token`
4. Use `{{base_url}}` and `{{auth_token}}` in requests

### Automated Tests

```bash
# Install test dependencies
pip install pytest pytest-django

# Run tests
pytest

# With coverage
pytest --cov=assessment --cov-report=html
```

---

## 🚀 Deployment

### Production Checklist

**1. Update settings.py:**

```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
SECRET_KEY = os.environ.get('SECRET_KEY')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        # ... PostgreSQL config
    }
}

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

**2. Collect static files:**

```bash
python manage.py collectstatic
```

**3. Use Gunicorn:**

```bash
pip install gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

**4. Set up Nginx:**

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /path/to/staticfiles/;
    }
}
```

**5. Use environment variables:**

```bash
export SECRET_KEY='your-secret-key'
export DATABASE_URL='postgresql://user:pass@localhost/db'
export DEBUG=False
```

---

## 🔧 Troubleshooting

### Issue: "no such table: assessment_course"

**Solution:**

```bash
python manage.py makemigrations
python manage.py migrate
```

### Issue: "Unable to log in with provided credentials"

**Solution:**

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
user = User.objects.get(username='testuser')
user.set_password('testpass123')
user.save()
exit()
```

### Issue: "Authentication credentials were not provided"

**Solution:** Check Authorization header format:

```
Authorization: Token abc123...
```

NOT:

```
Authorization: abc123...
```

### Issue: Swagger UI not loading

**Solution:** Simplify `SPECTACULAR_SETTINGS`:

```python
SPECTACULAR_SETTINGS = {
    'TITLE': 'Assessment Engine API',
    'VERSION': '1.0.0',
}
```

### Issue: Port already in use

**Solution:**

```bash
# Use different port
python manage.py runserver 8080

# Or find and kill process
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:8000 | xargs kill -9
```

---

## 📂 Project Structure

```
assessment_engine/
├── config/
│   ├── __init__.py
│   ├── settings.py          # Django settings
│   ├── urls.py              # Main URL routing
│   └── wsgi.py
├── assessment/
│   ├── migrations/
│   ├── __init__.py
│   ├── models.py            # Database models
│   ├── serializers.py       # DRF serializers
│   ├── views.py             # API views
│   ├── urls.py              # App URL routing
│   ├── admin.py             # Admin interface
│   ├── auth_views.py        # Custom auth views
│   └── grading_service.py   # Grading algorithms
├── manage.py
├── requirements.txt
├── create_sample_data.py
├── README.md
└── db.sqlite3
```

---

## 📞 Support & Contact

For issues or questions:

- Review API documentation at `/swagger/`
- Check logs in console output
- Verify authentication token format

---

## 📝 License

MIT License - Feel free to use for educational purposes.

---

**Built with ❤️ for Acad AI Backend Assessment**
