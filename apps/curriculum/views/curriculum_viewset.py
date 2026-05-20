from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.curriculum.models import Curriculum
from apps.curriculum.permissions import CanManageCurriculum, CanViewStudentUnits
from apps.curriculum.serializers import CurriculumSerializer
from apps.curriculum.services import CurriculumMapperService
from apps.curriculum.utils import get_user_department_id, is_department_admin, is_super_admin


class CurriculumListCreateAPIView(ListCreateAPIView):
    serializer_class = CurriculumSerializer
    permission_classes = [CanManageCurriculum]
    filterset_fields = ["program", "department", "academic_year", "study_year", "semester", "status"]

    def get_queryset(self):
        queryset = Curriculum.objects.select_related("program", "department", "created_by").prefetch_related(
            "curriculum_units",
            "version_history",
        )
        user = self.request.user
        if is_super_admin(user):
            return queryset

        if is_department_admin(user):
            return queryset.filter(department_id=get_user_department_id(user))

        return queryset.filter(status=Curriculum.Status.ACTIVE)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class CurriculumDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = CurriculumSerializer
    permission_classes = [CanManageCurriculum]

    def get_queryset(self):
        queryset = Curriculum.objects.select_related("program", "department", "created_by").prefetch_related(
            "curriculum_units",
            "version_history",
        )
        user = self.request.user
        if is_super_admin(user):
            return queryset
        if is_department_admin(user):
            return queryset.filter(department_id=get_user_department_id(user))
        return queryset.filter(status=Curriculum.Status.ACTIVE)


class StudentUnitsAPIView(APIView):
    permission_classes = [CanViewStudentUnits]

    def get(self, request):
        student = getattr(request.user, "student_profile", None)
        if not student:
            return Response(
                {"detail": "Student profile not found for the authenticated user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payload = CurriculumMapperService.get_required_units_for_student(student=student)
            return Response(payload, status=status.HTTP_200_OK)
        except DjangoValidationError as exc:
            detail = getattr(exc, "message", None) or "; ".join(getattr(exc, "messages", []))
            return Response({"detail": detail}, status=status.HTTP_400_BAD_REQUEST)


