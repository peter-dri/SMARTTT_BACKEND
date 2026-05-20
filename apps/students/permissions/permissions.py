"""
Student permissions module.

Implements role-based access control for student endpoints.

Access levels:
- Student: Can view own profile only
- Department Admin: Can manage students in their department
- Registrar/Super Admin: Full access
- Lecturer: Limited read-only access
"""

from rest_framework.permissions import BasePermission
from django.utils.translation import gettext_lazy as _

from apps.students.selectors import StudentSelector
from apps.students.utils import is_super_admin, is_department_admin, is_registrar, is_lecturer


class IsStudentOwnerOrAdmin(BasePermission):
    """
    Only student can view/edit their own profile, or admins can access.
    """

    message = _("You do not have permission to access this student profile.")

    def has_object_permission(self, request, view, obj):
        """Check if user has permission to access student object."""
        # Allow if user is the student themselves
        if hasattr(request.user, 'student_profile') and request.user.student_profile == obj:
            return True

        # Allow if user is admin
        if is_super_admin(request.user):
            return True

        # Allow if user is registrar
        if is_registrar(request.user):
            return True

        # Allow if user is department admin and student is in their department
        if is_department_admin(request.user):
            user_department_id = getattr(request.user, 'department_id', None)
            if user_department_id and obj.department_id == user_department_id:
                return True

        return False


class CanManageStudents(BasePermission):
    """
    Only department admins, registrars, and super admins can create/update/delete students.
    """

    message = _("You do not have permission to manage students.")

    def has_permission(self, request, view):
        """Check if user can manage students."""
        # Allow safe methods for authenticated users
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return request.user and request.user.is_authenticated

        # Only admins can modify
        if is_super_admin(request.user):
            return True

        if is_registrar(request.user):
            return True

        if is_department_admin(request.user):
            return True

        return False

    def has_object_permission(self, request, view, obj):
        """Check object-level permission."""
        # Allow safe methods for authenticated users
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return request.user and request.user.is_authenticated

        # Super admin can do anything
        if is_super_admin(request.user):
            return True

        # Registrar can do anything
        if is_registrar(request.user):
            return True

        # Department admin can only modify students in their department
        if is_department_admin(request.user):
            user_department_id = getattr(request.user, 'department_id', None)
            return user_department_id and obj.department_id == user_department_id

        return False


class CanViewStudentProfile(BasePermission):
    """
    Students can view own profile and academic info.
    Department admins can view students in their department.
    Admins can view all.
    """

    message = _("You do not have permission to view this profile.")

    def has_permission(self, request, view):
        """Check if user can access student endpoints."""
        # Only authenticated users
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Check object-level permission."""
        # Student viewing their own profile
        if hasattr(request.user, 'student_profile') and request.user.student_profile == obj:
            return True

        # Super admin
        if is_super_admin(request.user):
            return True

        # Registrar
        if is_registrar(request.user):
            return True

        # Department admin viewing their department
        if is_department_admin(request.user):
            user_department_id = getattr(request.user, 'department_id', None)
            return user_department_id and obj.department_id == user_department_id

        # Lecturer can view students in their courses (limited)
        if is_lecturer(request.user):
            # TODO: Implement course-based access
            return False

        return False


class CanUpdateOwnProfile(BasePermission):
    """
    Students can update limited fields in their own profile.
    Admins can update any student profile.
    """

    message = _("You do not have permission to update this profile.")

    def has_permission(self, request, view):
        """Check if user can update profiles."""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Check object-level permission."""
        # Student can edit their own profile (limited fields)
        if hasattr(request.user, 'student_profile') and request.user.student_profile == obj:
            # Limited fields only for student self-edit
            # This is handled in the view/serializer
            return True

        # Super admin can edit anyone
        if is_super_admin(request.user):
            return True

        # Registrar can edit anyone
        if is_registrar(request.user):
            return True

        # Department admin can edit their students
        if is_department_admin(request.user):
            user_department_id = getattr(request.user, 'department_id', None)
            return user_department_id and obj.department_id == user_department_id

        return False


class CanViewAcademicProgress(BasePermission):
    """
    Students can view their own progress.
    Department admins can view their department's progress.
    Admins can view all.
    """

    message = _("You do not have permission to view academic progress.")

    def has_permission(self, request, view):
        """Check if user can access progress endpoints."""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Check object-level permission."""
        # Student viewing their own progress
        if hasattr(request.user, 'student_profile') and request.user.student_profile == obj.student:
            return True

        # Super admin
        if is_super_admin(request.user):
            return True

        # Registrar
        if is_registrar(request.user):
            return True

        # Department admin viewing their department
        if is_department_admin(request.user):
            user_department_id = getattr(request.user, 'department_id', None)
            return user_department_id and obj.student.department_id == user_department_id

        return False


class CanManageEnrollments(BasePermission):
    """
    Only registrars, super admins, and department admins (for their department)
    can manage student enrollments.
    """

    message = _("You do not have permission to manage enrollments.")

    def has_permission(self, request, view):
        """Check if user can access enrollment endpoints."""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Check object-level permission."""
        # Super admin
        if is_super_admin(request.user):
            return True

        # Registrar
        if is_registrar(request.user):
            return True

        # Department admin for their department
        if is_department_admin(request.user):
            user_department_id = getattr(request.user, 'department_id', None)
            return user_department_id and obj.student.department_id == user_department_id

        return False


class IsDepartmentAdminOrSuper(BasePermission):
    """
    Permission for department-restricted operations.
    """

    message = _("You do not have permission to perform this action.")

    def has_permission(self, request, view):
        """Check if user is department admin or super admin."""
        if not request.user or not request.user.is_authenticated:
            return False

        return is_super_admin(request.user) or is_department_admin(request.user)
