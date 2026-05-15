"""Access helpers for personalization endpoints."""

from __future__ import annotations

from typing import Optional

from apps.accounts.models import User


def is_super_admin(user: User) -> bool:
	if not user or not user.is_authenticated:
		return False
	return bool(user.is_superuser)


def get_user_department_id(user: User) -> Optional[str]:
	if not user or not user.is_authenticated:
		return None

	lecturer_profile = getattr(user, "lecturer_profile", None)
	if lecturer_profile:
		return lecturer_profile.department_id

	student_profile = getattr(user, "student_profile", None)
	if student_profile:
		return student_profile.department_id

	return getattr(user, "department_id", None)


def is_department_admin(user: User) -> bool:
	if not user or not user.is_authenticated:
		return False
	return bool(getattr(user, "role", None) == User.Role.ADMIN and get_user_department_id(user))


def get_request_student(request):
	"""Return the logged-in student's profile if available."""
	return getattr(request.user, "student_profile", None)
