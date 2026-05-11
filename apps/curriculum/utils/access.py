from apps.accounts.models import User


def is_super_admin(user: User) -> bool:
    if not user or not user.is_authenticated:
        return False
    return bool(user.is_superuser)


def get_user_department_id(user: User):
    """Resolve department ownership for department-scoped admin users."""
    if not user or not user.is_authenticated:
        return None

    lecturer_profile = getattr(user, "lecturer_profile", None)
    if lecturer_profile:
        return lecturer_profile.department_id

    student_profile = getattr(user, "student_profile", None)
    if student_profile:
        return student_profile.program.department_id

    return None


def is_department_admin(user: User) -> bool:
    if not user or not user.is_authenticated:
        return False
    return bool(user.role == User.Role.ADMIN and get_user_department_id(user))