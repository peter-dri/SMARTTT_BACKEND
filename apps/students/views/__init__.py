from .student_viewset import StudentViewSet
from .views import (
    StudentProfileUpdateView,
    AcademicProgressViewSet,
    StudentEnrollmentViewSet,
)

__all__ = [
    "StudentViewSet",
    "StudentProfileUpdateView",
    "AcademicProgressViewSet",
    "StudentEnrollmentViewSet",
]
