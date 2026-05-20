"""Validation rules for personalization flows."""

from __future__ import annotations

from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from apps.curriculum.models import Curriculum
from apps.personalization.utils import is_department_admin, is_super_admin


class PersonalizationValidator:
	VALID_SEMESTERS = {1, 2}

	@staticmethod
	def validate_semester(semester):
		if semester is None:
			raise ValidationError({"semester": "semester is required."})
		try:
			semester_value = int(semester)
		except (TypeError, ValueError) as exc:
			raise ValidationError({"semester": "semester must be an integer."}) from exc
		if semester_value not in PersonalizationValidator.VALID_SEMESTERS:
			raise ValidationError({"semester": "semester must be 1 or 2."})
		return semester_value

	@staticmethod
	def validate_student(student):
		if student is None:
			raise NotFound("Student profile not found.")
		return student

	@staticmethod
	def validate_active_enrollment(enrollment_queryset):
		if not enrollment_queryset:
			raise NotFound("No active enrollment was found for the selected student.")
		return enrollment_queryset

	@staticmethod
	def validate_access(request_user, target_student):
		if not request_user or not request_user.is_authenticated:
			raise PermissionDenied("Authentication is required.")

		if is_super_admin(request_user):
			return True

		current_student = getattr(request_user, "student_profile", None)
		if current_student and current_student.id == target_student.id:
			return True

		if is_department_admin(request_user):
			user_department_id = getattr(request_user, "department_id", None)
			if user_department_id and target_student.department_id == user_department_id:
				return True

		raise PermissionDenied("You do not have access to this student's timetable.")

	@staticmethod
	def validate_timetable_sessions_exist(sessions):
		if not sessions:
			raise NotFound("No timetable sessions were found for the selected student.")
		return sessions

	@staticmethod
	def validate_curriculum(curriculum: Curriculum | None):
		if curriculum is None:
			raise NotFound("No active curriculum was found for the selected student.")
		return curriculum
