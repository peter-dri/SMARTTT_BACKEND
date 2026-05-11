from rest_framework import viewsets
from apps.units.models import Unit
from apps.units.serializers.serializers import UnitSerializer
from apps.departments.services.department_access_service import DepartmentAccessService


class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.select_related("department").all()
    serializer_class = UnitSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return self.queryset
        return self.queryset.filter(department__in=DepartmentAccessService.user_departments(user))
