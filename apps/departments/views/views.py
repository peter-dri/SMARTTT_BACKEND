from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from apps.departments.models import Faculty, Department, DepartmentAdmin
from apps.departments.serializers.serializers import FacultySerializer, DepartmentSerializer, DepartmentAdminSerializer
from apps.departments.permissions.permissions import IsDepartmentAdmin
from apps.departments.services.department_access_service import DepartmentAccessService


class FacultyViewSet(viewsets.ModelViewSet):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer
    permission_classes = []


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.select_related("faculty", "head_of_department").all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsDepartmentAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return self.queryset
        return DepartmentAccessService.user_departments(user)

    @action(detail=True, methods=["post"], url_path="assign-admin")
    def assign_admin(self, request, pk=None):
        department = DepartmentAccessService.ensure_user_has_access_to_department(request.user, pk)
        serializer = DepartmentAdminSerializer(data={"user": request.data.get("user"), "department": department.id, "role": request.data.get("role", "admin")})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DepartmentAdminViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DepartmentAdmin.objects.select_related("user", "department").all()
    serializer_class = DepartmentAdminSerializer
    permission_classes = [IsDepartmentAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return self.queryset
        return self.queryset.filter(department__in=DepartmentAccessService.user_departments(user))
