from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .views import (
    CourseViewSet, ExamViewSet, SubmissionViewSet, UserProfileViewSet
)

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'exams', ExamViewSet, basename='exam')
router.register(r'submissions', SubmissionViewSet, basename='submission')
router.register(r'users', UserProfileViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/', obtain_auth_token, name='api_token_auth'),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
]