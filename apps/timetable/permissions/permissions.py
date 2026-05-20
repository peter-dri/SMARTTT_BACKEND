from rest_framework.permissions import BasePermission
from django.utils.translation import gettext_lazy as _

from apps.accounts.utils import (
    is_super_admin,
    is_department_admin,
    is_registrar,
    is_lecturer,
    is_student,
)


class IsSuperAdminOrReadOnly(BasePermission):
    """Only super admin can modify. Others can read if authenticated."""

    message = _("Only administrators can perform this action")

    def has_permission(self, request, view):
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return request.user and request.user.is_authenticated
        return is_super_admin(request.user)


class IsDepartmentAdminOrSuper(BasePermission):
    """Department admin or super admin can manage."""

    message = _("Only department admins can perform this action")

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return is_department_admin(request.user) or is_super_admin(request.user)


class IsRegistrarOrSuper(BasePermission):
    """Registrar or super admin can manage."""

    message = _("Only registrars can perform this action")

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return is_registrar(request.user) or is_super_admin(request.user)


class CanManageTimetable(BasePermission):
    """
    Manage timetable sessions:
    - Super admin: manage all
    - Registrar: manage all
    - Department admin: manage own department only
    """

    message = _("You don't have permission to manage timetable sessions")

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True

        return (
            is_super_admin(request.user)
            or is_registrar(request.user)
            or is_department_admin(request.user)
        )

    def has_object_permission(self, request, view, obj):
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True

        if is_super_admin(request.user) or is_registrar(request.user):
            return True

        if is_department_admin(request.user):
            user_dept_id = getattr(request.user, "department_id", None)
            return obj.department_id == user_dept_id

        return False


class CanViewTimetable(BasePermission):
    """
    View timetable access:
    - Super admin/Registrar: view all
    - Department admin: view own department
    - Lecturer: view assigned sessions
    - Student: view personalized timetable
    """

    message = _("You don't have permission to view this timetable")

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if is_super_admin(request.user) or is_registrar(request.user):
            return True

        if is_department_admin(request.user):
            user_dept_id = getattr(request.user, "department_id", None)
            return obj.department_id == user_dept_id

        if is_lecturer(request.user):
            return obj.lecturer_id == getattr(request.user, "lecturer_profile", None)

        return True


class CanManageRooms(BasePermission):
    """Only super admin and registrar can manage rooms."""

    message = _("Only administrators can manage rooms")

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True

        return is_super_admin(request.user) or is_registrar(request.user)


class CanManageTimeSlots(BasePermission):
    """Only super admin and registrar can manage time slots."""

    message = _("Only administrators can manage time slots")

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True

        return is_super_admin(request.user) or is_registrar(request.user)


class IsLecturerOrAdmin(BasePermission):
    """Lecturer or admin access."""

    message = _("Only lecturers and administrators can access this")

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return (
            is_lecturer(request.user)
            or is_super_admin(request.user)
            or is_registrar(request.user)
        )


class IsStudentOrAdmin(BasePermission):
    """Student or admin access."""

    message = _("Only students and administrators can access this")

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return (
            is_student(request.user)
            or is_super_admin(request.user)
            or is_registrar(request.user)
        )
