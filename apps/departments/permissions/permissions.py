from rest_framework import permissions


class IsDepartmentAdmin(permissions.BasePermission):
    """Allow access only to department admins or superusers."""

    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            if request.user.is_superuser:
                return True
            return request.user.department_assignments.exists()
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        # obj is expected to be Department or related with department attribute
        department = getattr(obj, "department", None) or obj if hasattr(obj, "pk") else None
        if department is None:
            return False
        return department.admins.filter(user=request.user).exists()
