"""API views for personalized timetable intelligence."""

from __future__ import annotations

from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.personalization.services import PersonalizedTimetableService
from apps.personalization.utils import get_request_student, is_department_admin, is_super_admin
from apps.personalization.validators import PersonalizationValidator
from apps.students.models import Student


class BasePersonalizationAPIView(APIView):
	permission_classes = [IsAuthenticated]

	def resolve_student(self, request) -> Student:
		student_id = request.query_params.get("student_id")

		if student_id:
			student = (
				Student.objects.select_related("user", "department", "program", "program__department")
				.filter(id=student_id)
				.first()
			)
			student = PersonalizationValidator.validate_student(student)
			if not is_super_admin(request.user):
				if is_department_admin(request.user):
					user_department_id = getattr(request.user, "department_id", None)
					if not user_department_id or student.department_id != user_department_id:
						raise PermissionDenied("You do not have access to this student's timetable.")
				elif get_request_student(request) != student:
					raise PermissionDenied("You do not have access to this student's timetable.")
			return student

		student = get_request_student(request)
		if student is None:
			raise PermissionDenied("Student profile is required for this endpoint.")
		return PersonalizationValidator.validate_student(student)


class PersonalizedTimetableAPIView(BasePersonalizationAPIView):
	"""Return grouped timetable data for the resolved student."""

	def get(self, request, *args, **kwargs):
		student = self.resolve_student(request)
		PersonalizationValidator.validate_access(request.user, student)
		payload = PersonalizedTimetableService.generate_personalized_timetable(student)
		return Response(payload, status=status.HTTP_200_OK)


class PersonalizedUnitsAPIView(BasePersonalizationAPIView):
	"""Return the resolved units for the student."""

	def get(self, request, *args, **kwargs):
		student = self.resolve_student(request)
		PersonalizationValidator.validate_access(request.user, student)
		payload = PersonalizedTimetableService.generate_student_units_payload(student)
		return Response(payload, status=status.HTTP_200_OK)
