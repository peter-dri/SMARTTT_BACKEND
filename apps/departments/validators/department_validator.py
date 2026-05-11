from rest_framework.exceptions import ValidationError
from apps.departments.models import Faculty, Department


def validate_unique_faculty_code(code):
    if Faculty.objects.filter(code__iexact=code).exists():
        raise ValidationError(f"Faculty code '{code}' already exists.")


def validate_unique_department_code(faculty, code):
    if Department.objects.filter(faculty=faculty, code__iexact=code).exists():
        raise ValidationError(f"Department code '{code}' already exists in this faculty.")


def validate_department_admin_assignment(user, department):
    # prevent assigning the same user multiple times
    if department.admins.filter(user=user).exists():
        raise ValidationError("User is already assigned as a department admin.")
