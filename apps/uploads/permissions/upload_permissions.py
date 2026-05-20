from rest_framework.permissions import BasePermission
from django.utils.translation import gettext_lazy as _

from apps.curriculum.utils import get_user_department_id, is_department_admin, is_super_admin
from apps.students.utils import is_lecturer, is_registrar, is_student


def _upload_department_id(upload) -> str | None:
    if getattr(upload, "department_id", None):
        return upload.department_id
    program = getattr(upload, "program", None)
    if program and getattr(program, "department_id", None):
        return program.department_id
    return None


class CanManageTimetableUploads(BasePermission):
    message = _("You do not have permission to manage timetable uploads.")

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if is_super_admin(request.user) or is_registrar(request.user):
            return True
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return is_department_admin(request.user) or is_lecturer(request.user)
        return is_department_admin(request.user)

    def has_object_permission(self, request, view, obj):
        if is_super_admin(request.user) or is_registrar(request.user):
            return True
        if is_student(request.user):
            return False
        user_department_id = get_user_department_id(request.user)
        if not user_department_id:
            return False
        return _upload_department_id(obj) == user_department_id


class CanViewTimetableUploads(BasePermission):
    message = _("You do not have permission to view timetable uploads.")

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return not is_student(request.user)

    def has_object_permission(self, request, view, obj):
        if is_super_admin(request.user) or is_registrar(request.user):
            return True
        if is_lecturer(request.user):
            user_department_id = get_user_department_id(request.user)
            return user_department_id is not None and _upload_department_id(obj) == user_department_id
        if is_department_admin(request.user):
            user_department_id = get_user_department_id(request.user)
            return user_department_id is not None and _upload_department_id(obj) == user_department_id
        return False