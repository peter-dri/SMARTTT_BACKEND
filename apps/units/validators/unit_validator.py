from rest_framework.exceptions import ValidationError
from apps.units.models import Unit


def validate_unique_unit_code(department, code):
    if Unit.objects.filter(department=department, code__iexact=code).exists():
        raise ValidationError("Unit code already exists in this department.")


def validate_credit_hours(credit_hours):
    if credit_hours <= 0 or credit_hours > 30:
        raise ValidationError("Invalid credit hours.")


def validate_duplicate_unit_name(department, name):
    if Unit.objects.filter(department=department, name__iexact=name).exists():
        raise ValidationError("Unit name already exists in this department.")
