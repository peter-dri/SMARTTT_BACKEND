from .serializers import (
    StudentListSerializer,
    StudentDetailSerializer,
    StudentCreateUpdateSerializer,
    StudentProfileUpdateSerializer,
    StudentMyProfileSerializer,
    AcademicProgressSerializer,
    StudentEnrollmentSerializer,
)

__all__ = [
    "StudentListSerializer",
    "StudentDetailSerializer",
    "StudentCreateUpdateSerializer",
    "StudentProfileUpdateSerializer",
    "StudentMyProfileSerializer",
    "AcademicProgressSerializer",
    "StudentEnrollmentSerializer",
]

# Alias for backwards compatibility
StudentSerializer = StudentDetailSerializer
