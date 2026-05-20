from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.students.views import (
    StudentViewSet,
    StudentProfileUpdateView,
    AcademicProgressViewSet,
    StudentEnrollmentViewSet,
)

app_name = "students"

router = DefaultRouter()
router.register("students", StudentViewSet, basename="student")
router.register("academic-progress", AcademicProgressViewSet, basename="academic-progress")
router.register("enrollments", StudentEnrollmentViewSet, basename="enrollment")

urlpatterns = [
    path("", include(router.urls)),
    path("profile/me/update/", StudentProfileUpdateView.as_view(), name="profile-update"),
]
