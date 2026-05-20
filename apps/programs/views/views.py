from rest_framework import viewsets
from apps.programs.models import Program
from apps.programs.serializers.serializers import ProgramSerializer
from apps.departments.services.department_access_service import DepartmentAccessService


class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.select_related("department").all()
    serializer_class = ProgramSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return self.queryset
        # allow department admins to see programs in their departments
        return self.queryset.filter(department__in=DepartmentAccessService.user_departments(user))
