# Assessment Engine - Complete Testing Guide

## 📋 Table of Contents

1. [Pre-Test Setup](#pre-test-setup)
2. [Manual Testing with cURL](#manual-testing-with-curl)
3. [Testing with Swagger UI](#testing-with-swagger-ui)
4. [Testing with Postman](#testing-with-postman)
5. [Automated Test Script](#automated-test-script)
6. [Test Scenarios](#test-scenarios)
7. [Expected Results](#expected-results)
8. [Troubleshooting](#troubleshooting)

---

## 🔧 Pre-Test Setup

### Step 1: Verify Server is Running

```bash
# Navigate to project directory
cd assessment_engine

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Start server
python manage.py runserver 8080
```

**Expected Output:**

```
Starting development server at http://127.0.0.1:8080/
Quit the server with CTRL-BREAK.
```

### Step 2: Verify Database Has Sample Data

```bash
# In a new terminal, activate venv and run:
python manage.py shell
```

```python
from assessment.models import Course, Exam, Question, Submission
from django.contrib.auth.models import User

# Check data exists
print(f"Users: {User.objects.count()}")
print(f"Courses: {Course.objects.count()}")
print(f"Exams: {Exam.objects.count()}")
print(f"Questions: {Question.objects.count()}")

# Should show:
# Users: 2 (testuser, admin)
# Courses: 1 (CS101)
# Exams: 1 (Midterm Exam)
# Questions: 3

exit()
```

**If no data exists, run:**

```bash
python create_sample_data.py
```

### Step 3: Get Test Credentials

**Student Account:**

- Username: `testuser`
- Password: `testpass123`

**Admin Account:**

- Username: `admin`
- Password: `admin123`

---

## 🧪 Manual Testing with cURL

### Test 1: Authentication

#### 1.1 Get Authentication Token (Student)

**Request:**

```bash
curl -X POST http://127.0.0.1:8080/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'
```

**Expected Response (200 OK):**

```json
{
  "token": "bd5a146d946abd4a3951bcf9d24dd2cf4cdfa551",
  "user_id": 2,
  "username": "testuser",
  "email": "test@example.com"
}
```

**✅ Success Criteria:**

- Status code: 200
- Response contains `token` field
- Token is a 40-character string

**❌ Common Errors:**

```json
// Wrong credentials
{
  "non_field_errors": ["Unable to log in with provided credentials."]
}
```

**💾 Save Your Token:**

```bash
export TOKEN="YOUR_TOKEN_HERE"
# Or on Windows:
set TOKEN=YOUR_TOKEN_HERE
```

---

#### 1.2 Test Invalid Credentials

**Request:**

```bash
curl -X POST http://127.0.0.1:8080/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "wrongpassword"}'
```

**Expected Response (400 Bad Request):**

```json
{
  "non_field_errors": ["Unable to log in with provided credentials."]
}
```

---

### Test 2: User Profile

#### 2.1 Get Current User Profile

**Request:**

```bash
curl http://127.0.0.1:8080/api/users/me/ \
  -H "Authorization: Token $TOKEN"
```

**Expected Response (200 OK):**

```json
{
  "id": 2,
  "username": "testuser",
  "email": "test@example.com",
  "first_name": "Test",
  "last_name": "User"
}
```

**✅ Success Criteria:**

- Returns current authenticated user info
- Correct username and email

---

#### 2.2 Test Without Authentication

**Request:**

```bash
curl http://127.0.0.1:8080/api/users/me/
```

**Expected Response (401 Unauthorized):**

```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

### Test 3: Courses

#### 3.1 List All Courses

**Request:**

```bash
curl http://127.0.0.1:8080/api/courses/ \
  -H "Authorization: Token $TOKEN"
```

**Expected Response (200 OK):**

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
      "description": "Basic programming concepts and principles",
      "created_at": "2026-01-06T10:00:00Z"
    }
  ]
}
```

**✅ Success Criteria:**

- Status code: 200
- Returns paginated list of courses
- At least one course exists

---

#### 3.2 Get Course Details

**Request:**

```bash
curl http://127.0.0.1:8080/api/courses/1/ \
  -H "Authorization: Token $TOKEN"
```

**Expected Response (200 OK):**

```json
{
  "id": 1,
  "code": "CS101",
  "name": "Introduction to Computer Science",
  "description": "Basic programming concepts and principles",
  "created_at": "2026-01-06T10:00:00Z"
}
```

---

### Test 4: Exams

#### 4.1 List Available Exams

**Request:**

```bash
curl http://127.0.0.1:8080/api/exams/ \
  -H "Authorization: Token $TOKEN"
```

**Expected Response (200 OK):**

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "course": {
        "id": 1,
        "code": "CS101",
        "name": "Introduction to Computer Science"
      },
      "title": "Midterm Exam - OOP Fundamentals",
      "description": "Test your knowledge of Object Oriented Programming",
      "duration_minutes": 60,
      "total_marks": 35,
      "passing_score": 60.0,
      "status": "published",
      "is_active": true,
      "question_count": 3,
      "start_time": "2026-01-06T09:00:00Z",
      "end_time": "2026-01-13T09:00:00Z",
      "created_at": "2026-01-06T10:00:00Z"
    }
  ]
}
```

**✅ Success Criteria:**

- Only shows published exams
- `is_active` is true
- `question_count` matches actual questions

---

#### 4.2 Get Exam with Questions

**Request:**

```bash
curl http://127.0.0.1:8080/api/exams/1/ \
  -H "Authorization: Token $TOKEN"
```

**Expected Response (200 OK):**

```json
{
  "id": 1,
  "course": {
    "id": 1,
    "code": "CS101",
    "name": "Introduction to Computer Science"
  },
  "title": "Midterm Exam - OOP Fundamentals",
  "description": "Test your knowledge of Object Oriented Programming",
  "duration_minutes": 60,
  "total_marks": 35,
  "passing_score": 60.0,
  "status": "published",
  "start_time": "2026-01-06T09:00:00Z",
  "end_time": "2026-01-13T09:00:00Z",
  "is_active": true,
  "questions": [
    {
      "id": 1,
      "question_text": "What is polymorphism in Object Oriented Programming? Explain with examples.",
      "question_type": "essay",
      "marks": 20,
      "order": 1,
      "options": null
    },
    {
      "id": 2,
      "question_text": "What does OOP stand for?",
      "question_type": "short_answer",
      "marks": 10,
      "order": 2,
      "options": null
    },
    {
      "id": 3,
      "question_text": "Python is a compiled language.",
      "question_type": "true_false",
      "marks": 5,
      "order": 3,
      "options": ["true", "false"]
    }
  ],
  "created_at": "2026-01-06T10:00:00Z"
}
```

**✅ Success Criteria:**

- Questions array is populated
- Questions are ordered by `order` field
- Expected answers are NOT exposed
- Question types include essay, short_answer, true_false

**❌ Security Check:**

- Verify `expected_answer` field is NOT in response
- Verify `grading_rubric` is NOT exposed

---

#### 4.3 Start Exam (Optional Tracking)

**Request:**

```bash
curl -X POST http://127.0.0.1:8080/api/exams/1/start/ \
  -H "Authorization: Token $TOKEN"
```

**Expected Response (201 Created):**

```json
{
  "submission_id": 1,
  "started_at": "2026-01-06T10:30:00Z",
  "exam": {
    "id": 1,
    "title": "Midterm Exam - OOP Fundamentals",
    ...
  }
}
```

**✅ Success Criteria:**

- Creates submission record with status "in_progress"
- Returns submission_id for tracking

**If Already Started:**

```json
{
  "error": "You have already started this exam",
  "submission_id": 1
}
```

---

### Test 5: Submissions (MAIN TEST)

#### 5.1 Submit Exam - Good Answers (Should PASS)

**Request:**

```bash
curl -X POST http://127.0.0.1:8080/api/submissions/submit/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "exam_id": 1,
    "answers": [
      {
        "question_id": 1,
        "answer_text": "Polymorphism is the ability of objects to take multiple forms. It allows methods to do different things based on the object type. For example, a Shape class can have a draw method, and Circle and Square subclasses can implement it differently, enabling code reusability and flexibility in object-oriented design."
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
  }'
```

**Expected Response (201 Created):**

```json
{
  "id": 1,
  "exam": {
    "id": 1,
    "title": "Midterm Exam - OOP Fundamentals",
    "total_marks": 35
  },
  "student_name": "Test User",
  "student_username": "testuser",
  "status": "graded",
  "started_at": "2026-01-06T10:30:00Z",
  "submitted_at": "2026-01-06T10:45:00Z",
  "graded_at": "2026-01-06T10:45:02Z",
  "score": 33.5,
  "percentage": 95.71,
  "is_passed": true,
  "feedback": "Congratulations! You passed with 95.71%",
  "grading_metadata": {
    "grading_method": "automated",
    "graded_at": "2026-01-06T10:45:02.123456"
  },
  "answers": [
    {
      "id": 1,
      "question": {
        "id": 1,
        "question_text": "What is polymorphism in Object Oriented Programming?",
        "question_type": "essay",
        "marks": 20,
        "order": 1
      },
      "answer_text": "Polymorphism is the ability of objects to take multiple forms...",
      "score": 18.5,
      "feedback": "Excellent answer with strong alignment to expected content.",
      "grading_details": {
        "strategy": "cosine_similarity",
        "similarity_score": 0.88,
        "adjusted_similarity": 0.94,
        "student_word_count": 45,
        "expected_word_count": 38
      },
      "created_at": "2026-01-06T10:45:00Z"
    },
    {
      "id": 2,
      "question": {
        "id": 2,
        "question_text": "What does OOP stand for?",
        "question_type": "short_answer",
        "marks": 10,
        "order": 2
      },
      "answer_text": "Object Oriented Programming",
      "score": 10.0,
      "feedback": "Good coverage of key concepts: object, oriented, programming",
      "grading_details": {
        "strategy": "keyword_matching",
        "matched_keywords": ["object", "oriented", "programming"],
        "missed_keywords": [],
        "match_percentage": 100.0,
        "word_count": 3,
        "length_factor": 1.0
      },
      "created_at": "2026-01-06T10:45:00Z"
    },
    {
      "id": 3,
      "question": {
        "id": 3,
        "question_text": "Python is a compiled language.",
        "question_type": "true_false",
        "marks": 5,
        "order": 3
      },
      "answer_text": "false",
      "score": 5.0,
      "feedback": "Correct!",
      "grading_details": {
        "strategy": "mcq",
        "is_correct": true,
        "student_answer": "false",
        "expected_answer": "false"
      },
      "created_at": "2026-01-06T10:45:00Z"
    }
  ]
}
```

**✅ Success Criteria:**

- Status code: 201
- `status` is "graded"
- `score` is calculated (should be ~30-35)
- `percentage` is calculated
- `is_passed` is true (percentage >= 60%)
- `feedback` message says "Congratulations!"
- Each answer has individual `score` and `feedback`
- `grading_details` shows which algorithm was used
- Grading happened immediately (within seconds)

---

#### 5.2 Submit Exam - Poor Answers (Should FAIL)

**Request:**

```bash
curl -X POST http://127.0.0.1:8080/api/submissions/submit/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "exam_id": 1,
    "answers": [
      {
        "question_id": 1,
        "answer_text": "I dont know"
      },
      {
        "question_id": 2,
        "answer_text": "OOP"
      },
      {
        "question_id": 3,
        "answer_text": "true"
      }
    ]
  }'
```

**Expected Response (201 Created but LOW SCORE):**

```json
{
  "id": 2,
  "status": "graded",
  "score": 3.5,
  "percentage": 10.0,
  "is_passed": false,
  "feedback": "You scored 10.0%. Passing score is 60.0%",
  "answers": [
    {
      "question": {...},
      "score": 0.5,
      "feedback": "Answer needs significant improvement. Review the question carefully."
    },
    {
      "question": {...},
      "score": 3.0,
      "feedback": "Good coverage of key concepts: programming. Consider including: object, oriented"
    },
    {
      "question": {...},
      "score": 0.0,
      "feedback": "Incorrect. Expected: false"
    }
  ]
}
```

**✅ Success Criteria:**

- Low score (< 21 out of 35)
- `is_passed` is false
- Feedback suggests improvement
- Individual answers have constructive feedback

---

#### 5.3 Test Validation - Invalid Exam ID

**Request:**

```bash
curl -X POST http://127.0.0.1:8080/api/submissions/submit/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "exam_id": 999,
    "answers": [
      {"question_id": 1, "answer_text": "test"}
    ]
  }'
```

**Expected Response (400 Bad Request):**

```json
{
  "exam_id": ["Invalid exam ID"]
}
```

---

#### 5.4 Test Validation - Questions Don't Belong to Exam

**Request:**

```bash
curl -X POST http://127.0.0.1:8080/api/submissions/submit/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "exam_id": 1,
    "answers": [
      {"question_id": 999, "answer_text": "test"}
    ]
  }'
```

**Expected Response (400 Bad Request):**

```json
{
  "non_field_errors": ["Some questions do not belong to this exam"]
}
```

---

#### 5.5 Test Duplicate Submission Prevention

**Request:** (Submit the same exam twice)

```bash
# First submission - should work
curl -X POST http://127.0.0.1:8080/api/submissions/submit/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "exam_id": 1,
    "answers": [
      {"question_id": 1, "answer_text": "test"},
      {"question_id": 2, "answer_text": "test"},
      {"question_id": 3, "answer_text": "false"}
    ]
  }'

# Second submission - should fail
curl -X POST http://127.0.0.1:8080/api/submissions/submit/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "exam_id": 1,
    "answers": [
      {"question_id": 1, "answer_text": "test2"},
      {"question_id": 2, "answer_text": "test2"},
      {"question_id": 3, "answer_text": "false"}
    ]
  }'
```

**Expected Response (400 Bad Request):**

```json
{
  "error": "This exam has already been submitted"
}
```

---

#### 5.6 Test Wrong Endpoint (Should Give Helpful Error)

**Request:**

```bash
curl -X POST http://127.0.0.1:8080/api/submissions/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "exam_id": 1,
    "answers": []
  }'
```

**Expected Response (405 Method Not Allowed):**

```json
{
  "error": "Direct submission creation is not allowed. Use /api/submissions/submit/ endpoint instead.",
  "correct_endpoint": "/api/submissions/submit/",
  "method": "POST",
  "example": {
    "exam_id": 1,
    "answers": [
      {
        "question_id": 1,
        "answer_text": "Your answer here"
      }
    ]
  }
}
```

**✅ Success Criteria:**

- Clear error message
- Provides correct endpoint
- Includes usage example

---

### Test 6: View Submissions

#### 6.1 List Your Submissions

**Request:**

```bash
curl http://127.0.0.1:8080/api/submissions/ \
  -H "Authorization: Token $TOKEN"
```

**Expected Response (200 OK):**

```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 2,
      "exam": {
        "id": 1,
        "title": "Midterm Exam - OOP Fundamentals"
      },
      "student_name": "Test User",
      "student_username": "testuser",
      "status": "graded",
      "started_at": "2026-01-06T11:00:00Z",
      "submitted_at": "2026-01-06T11:15:00Z",
      "graded_at": "2026-01-06T11:15:02Z",
      "score": 10.0,
      "percentage": 28.57,
      "is_passed": false
    },
    {
      "id": 1,
      "exam": {
        "id": 1,
        "title": "Midterm Exam - OOP Fundamentals"
      },
      "student_name": "Test User",
      "student_username": "testuser",
      "status": "graded",
      "started_at": "2026-01-06T10:30:00Z",
      "submitted_at": "2026-01-06T10:45:00Z",
      "graded_at": "2026-01-06T10:45:02Z",
      "score": 33.5,
      "percentage": 95.71,
      "is_passed": true
    }
  ]
}
```

**✅ Success Criteria:**

- Only shows current user's submissions
- Results ordered by submission time (newest first)

---

#### 6.2 Get Specific Submission Details

**Request:**

```bash
curl http://127.0.0.1:8080/api/submissions/1/ \
  -H "Authorization: Token $TOKEN"
```

**Expected Response (200 OK):**

- Full submission details
- All answers with individual scores
- Grading details for each answer

---

#### 6.3 Test Ownership Enforcement (Security Test)

**Create second user and try to access first user's submission:**

```bash
# Get token for different user (create one first if needed)
curl -X POST http://127.0.0.1:8080/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Try to access testuser's submission (id=1) as admin
curl http://127.0.0.1:8080/api/submissions/1/ \
  -H "Authorization: Token ADMIN_TOKEN"
```

**Expected for Regular User (404 Not Found):**

```json
{
  "detail": "Not found."
}
```

**Expected for Admin (200 OK):**

- Admins CAN see all submissions
- This verifies the permission system works

---

#### 6.4 View Results with Statistics

**Request:**

```bash
curl http://127.0.0.1:8080/api/submissions/my_results/ \
  -H "Authorization: Token $TOKEN"
```

**Expected Response (200 OK):**

```json
{
  "statistics": {
    "total_exams": 2,
    "passed_exams": 1,
    "failed_exams": 1,
    "average_percentage": 62.14,
    "pass_rate": 50.0
  },
  "submissions": [
    {
      "id": 2,
      "exam": {...},
      "score": 10.0,
      "percentage": 28.57,
      "is_passed": false
    },
    {
      "id": 1,
      "exam": {...},
      "score": 33.5,
      "percentage": 95.71,
      "is_passed": true
    }
  ]
}
```

**✅ Success Criteria:**

- Statistics calculated correctly:
  - `total_exams` = count of graded submissions
  - `passed_exams` = count where percentage >= passing_score
  - `average_percentage` = mean of all percentages
  - `pass_rate` = (passed / total) × 100

---

### Test 7: Admin Features

#### 7.1 Regrade Submission (Admin Only)

**Request:**

```bash
# First get admin token
ADMIN_TOKEN=$(curl -s -X POST http://127.0.0.1:8080/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' \
  | grep -o '"token":"[^"]*' | cut -d'"' -f4)

# Regrade a submission
curl -X POST http://127.0.0.1:8080/api/submissions/1/regrade/ \
  -H "Authorization: Token $ADMIN_TOKEN"
```

**Expected Response (200 OK):**

- Returns re-graded submission
- New `graded_at` timestamp
- Scores may change if grading algorithm updated

**As Regular User (403 Forbidden):**

```bash
curl -X POST http://127.0.0.1:8080/api/submissions/1/regrade/ \
  -H "Authorization: Token $TOKEN"
```

**Expected:**

```json
{
  "detail": "Only staff can regrade submissions"
}
```

---

## 🎨 Testing with Swagger UI

### Access Swagger

1. Open browser: http://127.0.0.1:8080/swagger/
2. You'll see interactive API documentation

### Step-by-Step Swagger Test

#### 1. Get Authentication Token

1. Find: **POST `/api/auth/token/`**
2. Click **"Try it out"**
3. Enter request body:
   ```json
   {
     "username": "testuser",
     "password": "testpass123"
   }
   ```
4. Click **"Execute"**
5. **Copy the token** from response

#### 2. Authorize in Swagger

1. Click **"Authorize"** button (🔒 lock icon at top)
2. Enter: `Token YOUR_TOKEN_HERE`
   - Example: `Token bd5a146d946abd4a3951bcf9d24dd2cf4cdfa551`
3. Click **"Authorize"**
4. Click **"Close"**

#### 3. Test Endpoints

Now all endpoints will include your token automatically!

**Test in this order:**

1. `GET /api/courses/` - View courses
2. `GET /api/exams/` - View exams
3. `GET /api/exams/1/` - Get exam questions
4. `POST /api/submissions/submit/` - Submit exam
5. `GET /api/submissions/my_results/` - View results

### Common Swagger Issues

**Issue: Execute button doesn't work**

- Clear browser cache
- Try different browser
- Use cURL instead

**Issue: "Failed to load API definition"**

- Server might have errors
- Check terminal for Django errors
- Restart server

**Issue: Getting 401 Unauthorized**

- Authorization format must be: `Token abc123...` (with "Token" prefix)
- Token must be from `/api/auth/token/` endpoint
- Don't forget the space after "Token"

---

## 📮 Testing with Postman

### Setup Postman Collection

#### 1. Create New Collection

1. Open Postman
2. Click **"New"** → **"Collection"**
3. Name: "Assessment Engine API"

#### 2. Set Variables

1. Click on collection → **"Variables"** tab
2. Add variables:
   - `base_url`: `http://127.0.0.1:8080/api`
   - `token`: (leave empty, will be set after login)

#### 3. Add Requests

**Request 1: Get Token**

- Method: `POST`
- URL: `{{base_url}}/auth/token/`
- Body (JSON):
  ```json
  {
    "username": "testuser",
    "password": "testpass123"
  }
  ```
- Tests (auto-save token):
  ```javascript
  var jsonData = pm.response.json();
  pm.collectionVariables.set("token", jsonData.token);
  ```

**Request 2: List Exams**

- Method: `GET`
- URL: `{{base_url}}/exams/`
- Headers:
  - Key: `Authorization`
  - Value: `Token {{token}}`

**Request 3: Submit Exam**

- Method: `POST`
- URL: `{{base_url}}/submissions/submit/`
- Headers:
  - Key: `Authorization`
  - Value: `Token {{token}}`
  - Key: `Content-Type`
  - Value: `application/json`
- Body (JSON):
  ```json
  {
    "exam_id": 1,
    "answers": [
      {
        "question_id": 1,
        "answer_text": "Polymorphism allows objects to take multiple forms"
      },
      { "question_id": 2, "answer_text": "Object Oriented Programming" },
      { "question_id": 3, "answer_text": "false" }
    ]
  }
  ```

#### 4. Run Collection

1. Click **"Run collection"**
2. Select all requests
3. Click **"Run Assessment Engine API"**
4. View results

---

## 🤖 Automated Test Script

### Bash Script (Linux/Mac/Git Bash)

Save as `test_api.sh`:

```bash
#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

BASE_URL="http://127.0.0.1:8080/api"

echo "🧪 Assessment Engine API Test Suite"
echo "====================================="
echo ""

# Test 1: Get Token
echo -n "Test 1: Authentication... "
TOKEN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/token/" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}')

TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo -e "${RED}FAILED${NC}"
    echo "Response: $TOKEN_RESPONSE"
    exit 1
else
    echo -e "${GREEN}PASSED${NC}"
    echo "  Token: ${TOKEN:0:20}..."
fi

# Test 2: List Courses
echo -n "Test 2: List Courses... "
COURSES_RESPONSE=$(curl -s "$BASE_URL/courses/" \
  -H "
```
