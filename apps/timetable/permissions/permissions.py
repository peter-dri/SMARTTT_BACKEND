"""
Permission classes for timetable management.

Production-level permissions with clear separation of concerns:
- Admin and staff can manage timetable uploads and sessions
- Students and lecturers can view their own timetable slots
"""

from rest_framework.permissions import BasePermission, DjangoModelPermissions


class CanManageTimetable(DjangoModelPermissions):
    """
    Allow admin/staff users to manage timetable uploads and sessions.
    
    Permissions checked:
    - add_timetableuploadbatch
    - change_timetableuploadbatch
    - delete_timetableuploadbatch
    - view_timetableslot
    """
    
    perms_map = {
        'GET': ['timetable.view_timetableuploadbatch', 'timetable.view_timetableslot'],
        'POST': ['timetable.add_timetableuploadbatch'],
        'PUT': ['timetable.change_timetableuploadbatch'],
        'PATCH': ['timetable.change_timetableuploadbatch'],
        'DELETE': ['timetable.delete_timetableuploadbatch'],
    }

    def has_permission(self, request, view):
        # Allow read-only access if user is authenticated
        if request.method == 'GET':
            return request.user and request.user.is_authenticated
        
        # Allow write access only to admin/staff
        if request.user and request.user.is_authenticated:
            return request.user.is_staff or request.user.is_superuser
        
        return False


class CanViewOwnTimetable(BasePermission):
    """
    Allow students and lecturers to view only their own timetable slots.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Students can only view slots for their program
        if hasattr(request.user, 'student'):
            student = request.user.student
            return obj.curriculum_unit.curriculum.program in student.programs.all()
        
        # Lecturers can only view their own slots
        if hasattr(request.user, 'lecturer'):
            lecturer = request.user.lecturer
            return obj.lecturer == lecturer
        
        # Admin/Staff can view all
        return request.user.is_staff or request.user.is_superuser
