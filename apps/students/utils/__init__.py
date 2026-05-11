"""
Student utilities module.

Helper functions for common operations needed across the students app.
"""

from typing import Optional
from django.core.exceptions import ObjectDoesNotExist


def is_super_admin(user) -> bool:
    """
    Check if user is a super admin.

    Args:
        user: User instance to check

    Returns:
        True if user is super admin, False otherwise
    """
    if not user or not hasattr(user, 'role'):
        return False
    return user.role == 'admin' and user.is_staff and user.is_superuser


def is_department_admin(user) -> bool:
    """
    Check if user is a department administrator.

    Args:
        user: User instance to check

    Returns:
        True if user is department admin, False otherwise
    """
    if not user or not hasattr(user, 'role'):
        return False
    return user.role == 'admin' or user.role == 'registrar'


def is_registrar(user) -> bool:
    """
    Check if user is a registrar.

    Args:
        user: User instance to check

    Returns:
        True if user is registrar, False otherwise
    """
    if not user or not hasattr(user, 'role'):
        return False
    return user.role == 'registrar'


def is_lecturer(user) -> bool:
    """
    Check if user is a lecturer.

    Args:
        user: User instance to check

    Returns:
        True if user is lecturer, False otherwise
    """
    if not user or not hasattr(user, 'role'):
        return False
    return user.role == 'lecturer'


def is_student(user) -> bool:
    """
    Check if user is a student.

    Args:
        user: User instance to check

    Returns:
        True if user is student, False otherwise
    """
    if not user or not hasattr(user, 'role'):
        return False
    return user.role == 'student'


def get_user_department_id(user) -> Optional[str]:
    """
    Get department ID for a user if they belong to a department.

    Args:
        user: User instance

    Returns:
        Department ID if user is associated with a department, None otherwise
    """
    try:
        if hasattr(user, 'student_profile'):
            return user.student_profile.department_id
        if hasattr(user, 'department_id'):
            return user.department_id
    except (AttributeError, ObjectDoesNotExist):
        pass
    return None


def get_student_full_name(student) -> str:
    """
    Get student's full name.

    Args:
        student: Student instance

    Returns:
        Student's full name
    """
    if hasattr(student, 'get_full_name'):
        return student.get_full_name()
    return f"{student.first_name} {student.last_name}".strip()


def format_academic_year(admission_year: int, study_year: int) -> str:
    """
    Format academic year string.

    Args:
        admission_year: Year of admission
        study_year: Current study year

    Returns:
        Formatted academic year (e.g., '2024/2025')
    """
    current_year = admission_year + study_year - 1
    return f"{current_year}/{current_year + 1}"


def calculate_study_year(admission_year: int, current_year: int) -> int:
    """
    Calculate current study year based on admission year.

    Args:
        admission_year: Year student was admitted
        current_year: Current year

    Returns:
        Current study year (1-based)
    """
    study_year = current_year - admission_year + 1
    return max(1, study_year)  # Ensure minimum 1


def is_student_eligible_for_graduation(student) -> bool:
    """
    Determine if student is eligible for graduation.

    Args:
        student: Student instance

    Returns:
        True if student can graduate, False otherwise
    """
    if not hasattr(student, 'program'):
        return False

    return student.current_study_year > student.program.duration_years


def get_pagination_params(request, default_limit: int = 20) -> tuple:
    """
    Extract pagination parameters from request.

    Args:
        request: HTTP request object
        default_limit: Default number of items per page

    Returns:
        Tuple of (limit, offset)
    """
    try:
        limit = int(request.query_params.get('limit', default_limit))
        offset = int(request.query_params.get('offset', 0))

        # Validate limits
        limit = min(limit, 100)  # Max 100 items per page
        limit = max(limit, 1)    # Min 1 item per page
        offset = max(offset, 0)  # Min 0 offset

        return limit, offset
    except (ValueError, TypeError):
        return default_limit, 0
