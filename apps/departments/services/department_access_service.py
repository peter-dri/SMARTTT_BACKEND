from django.shortcuts import get_object_or_404
from apps.departments.models import Department, DepartmentAdmin


class DepartmentAccessService:
    """Service to resolve department context and apply department-level isolation."""

    @staticmethod
    def user_departments(user):
        if user.is_superuser:
            return Department.objects.all()
        return Department.objects.filter(admins__user=user)

    @staticmethod
    def user_primary_department(user):
        qs = Department.objects.filter(admins__user=user)
        return qs.first()

    @staticmethod
    def ensure_user_has_access_to_department(user, department_id):
        if user.is_superuser:
            return get_object_or_404(Department, pk=department_id)
        return get_object_or_404(Department, pk=department_id, admins__user=user)
