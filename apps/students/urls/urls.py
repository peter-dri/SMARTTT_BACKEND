"""
Student API URL routing.

Configures all endpoints for the students module.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.students.views import (
    StudentViewSet,
    StudentProfileUpdateView,
    AcademicProgressViewSet,
    StudentEnrollmentViewSet,
)

app_name = 'students'

# Register viewsets with router
router = DefaultRouter()
router.register(r'students', StudentViewSet, basename='student')
router.register(r'academic-progress', AcademicProgressViewSet, basename='academic-progress')
router.register(r'enrollments', StudentEnrollmentViewSet, basename='enrollment')

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),

    # Additional custom endpoints
    path('profile/me/update/', StudentProfileUpdateView.as_view(), name='profile-update'),
]
