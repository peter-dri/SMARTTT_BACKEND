from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from apps.curriculum.models import Curriculum
from apps.curriculum.serializers.serializers import CurriculumSerializer
from apps.curriculum.services.curriculum_mapper import CurriculumMapper
from apps.programs.models import Program


class CurriculumViewSet(viewsets.ModelViewSet):
    queryset = Curriculum.objects.select_related("program").all()
    serializer_class = CurriculumSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return self.queryset
        # allow department admins to view curriculums within their departments
        return self.queryset.filter(program__department__in=self.request.user.department_assignments.values_list("department", flat=True))


class StudentUnitsView(APIView):
    """Return units for the logged in student based on their program/year/semester.

    The view attempts to detect student info from the user profile and falls back to query params `program_id`, `study_year`, `semester`.
    """

    def get(self, request):
        user = request.user
        program = None
        study_year = request.query_params.get("study_year")
        semester = request.query_params.get("semester")
        program_id = request.query_params.get("program_id")

        # Attempt to discover from user's profile (common pattern)
        profile = getattr(user, "student_profile", None)
        if profile:
            program = profile.program
            study_year = study_year or profile.current_study_year
            semester = semester or profile.current_semester

        if program_id and not program:
            program = Program.objects.filter(pk=program_id).first()

        if not program or not study_year or not semester:
            return Response({"detail": "Missing program/study_year/semester information"}, status=status.HTTP_400_BAD_REQUEST)

        units = CurriculumMapper.determine_units_for_student(program, int(study_year), int(semester))
        data = [{"id": u.id, "code": u.code, "name": u.name, "credit_hours": str(u.credit_hours)} for u in units]
        return Response({"program": str(program), "study_year": study_year, "semester": semester, "units": data})
