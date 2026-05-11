from rest_framework.exceptions import ValidationError
from apps.programs.models import Program


def validate_unique_program_code(department, code):
    if Program.objects.filter(department=department, code__iexact=code).exists():
        raise ValidationError("Program code already exists in this department.")


def validate_program_duration(duration_years):
    if duration_years < 1 or duration_years > 10:
        raise ValidationError("Invalid program duration. Must be between 1 and 10 years.")


def validate_duplicate_program(department, name):
    if Program.objects.filter(department=department, name__iexact=name).exists():
        raise ValidationError("Program with this name already exists in the department.")
