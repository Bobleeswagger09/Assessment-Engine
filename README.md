🧠 Mini Assessment Engine (Acad AI)A robust Django REST Framework backend designed to handle automated academic evaluations. This engine supports multi-type questions, instant grading feedback, and student performance analytics.🚀 Core Features🔐 Secure Authentication: Token-based system with strict role-based access control (RBAC).📚 Course & Exam Management: Relational structure linking Courses -> Exams -> Questions.🤖 Automated Grading: Instant evaluation using keyword matching and similarity logic.📊 Performance Analytics: Real-time calculation of pass rates, averages, and historical trends.🧾 API Documentation: Interactive Swagger/OpenAPI 3.0 UI for rapid testing.🛡️ Data Integrity: Prevents duplicate submissions and protects answer keys from being exposed in the frontend.🏗️ Technical ArchitectureKey Components:grading_service.py: A decoupled service layer that handles the evaluation logic for Essay, Short Answer, and MCQ/TF questions.permissions.py: Custom permission classes to ensure students only access their own results while admins retain full oversight.Serializers: Optimized to provide "Question-only" views during exams and "Detailed-feedback" views post-submission.🛠️ Installation & Local Setup1. Environment SetupBash# Clone the repository
git clone https://github.com/your-username/assessment-engine.git
cd assessment-engine

# Create and activate virtual environment

python -m venv venv
source venv/bin/activate # macOS/Linux

# venv\Scripts\activate # Windows

# Install dependencies

pip install -r requirements.txt 2. Database InitializationBashpython manage.py migrate
python create_sample_data.py # Seeds the DB with test courses and exams
python manage.py runserver 8080
🧪 Testing Guide1. Swagger UI (Recommended)Navigate to http://127.0.0.1:8080/swagger/ to interact with the API directly.Use /api/auth/token/ to get your key.Click Authorize and enter: Token <your_token_here>.2. Manual cURL Test (Submission Flow)Bashcurl -X POST http://127.0.0.1:8080/api/submissions/submit/ \
 -H "Authorization: Token YOUR_TOKEN" \
 -H "Content-Type: application/json" \
 -d '{
"exam_id": 1,
"answers": [
{"question_id": 1, "answer_text": "Polymorphism allows objects to take multiple forms."},
{"question_id": 2, "answer_text": "Object Oriented Programming"},
{"question_id": 3, "answer_text": "false"}
]
}'
📡 API Endpoints SummaryMethodEndpointDescriptionAccessPOST/api/auth/token/Login & get TokenPublicGET/api/exams/List available examsStudent/AdminGET/api/exams/{id}/Get questions (Answers hidden)Student/AdminPOST/api/submissions/submit/Submit exam for gradingStudentGET/api/submissions/my_results/Get pass rate & statsStudentPOST/api/submissions/{id}/regrade/Manually trigger regradingAdmin Only☁️ DeploymentThis project is configured for easy deployment on Render, Railway, or Heroku using Gunicorn and WhiteNoise for static files.📄 LicenseDistributed under the MIT License. See LICENSE for more information.✨ Author: Victor Samuel
