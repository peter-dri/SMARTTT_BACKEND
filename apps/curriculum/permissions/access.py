from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.curriculum.utils import get_user_department_id, is_department_admin, is_super_admin


class CanManageCurriculum(BasePermission):
    """Allows super admins full access and department admins scoped write access."""

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True

        return is_super_admin(user) or is_department_admin(user)

    def has_object_permission(self, request, view, obj):
        user = request.user

        if request.method in SAFE_METHODS:
            if is_super_admin(user):
                return True
            if getattr(user, "role", None) == "student":
                return True
            if is_department_admin(user):
                return obj.department_id == get_user_department_id(user)
            return False

        if is_super_admin(user):
            return True

        if is_department_admin(user):
            return obj.department_id == get_user_department_id(user)

        return False


class CanViewStudentUnits(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return bool(getattr(user, "role", None) == "student" or is_super_admin(user))