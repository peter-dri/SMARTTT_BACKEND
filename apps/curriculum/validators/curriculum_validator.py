from rest_framework.exceptions import ValidationError
from apps.curriculum.models import Curriculum, CurriculumUnit


def validate_no_duplicate_units(curriculum, unit):
    if CurriculumUnit.objects.filter(curriculum=curriculum, unit=unit).exists():
        raise ValidationError("Unit is already assigned to this curriculum.")


def validate_duplicate_curriculum_version(program, academic_year, study_year, semester, version):
    if Curriculum.objects.filter(program=program, academic_year=academic_year, study_year=study_year, semester=semester, version=version).exists():
        raise ValidationError("Curriculum version already exists for this program/study year/semester.")


def validate_semester_value(semester):
    if semester < 1 or semester > 3:
        raise ValidationError("Invalid semester value.")


def validate_required_units_present(curriculum):
    core_count = CurriculumUnit.objects.filter(curriculum=curriculum, is_core=True).count()
    if core_count == 0:
        raise ValidationError("Curriculum must contain at least one core unit.")
from collections import Counter

from django.core.exceptions import ValidationError

from apps.curriculum.models import Curriculum, CurriculumUnit


class CurriculumDomainValidator:
    """Validates curriculum payloads and cross-entity integrity constraints."""

    @staticmethod
    def validate_semester(semester: int) -> None:
        if semester not in (1, 2, 3):
            raise ValidationError({"semester": "Invalid semester. Allowed values are 1, 2, 3."})

    @staticmethod
    def validate_duplicate_units(units_payload: list[dict]) -> None:
        unit_ids = [item.get("unit") for item in units_payload if item.get("unit")]
        duplicates = [unit_id for unit_id, count in Counter(unit_ids).items() if count > 1]
        if duplicates:
            raise ValidationError({"units": f"Duplicate units in payload: {duplicates}"})

    @staticmethod
    def validate_duplicate_curriculum_version(
        *,
        program_id,
        academic_year: str,
        study_year: int,
        semester: int,
        version: int,
        exclude_curriculum_id=None,
    ) -> None:
        queryset = Curriculum.objects.filter(
            program_id=program_id,
            academic_year=academic_year,
            study_year=study_year,
            semester=semester,
            version=version,
        )
        if exclude_curriculum_id:
            queryset = queryset.exclude(id=exclude_curriculum_id)

        if queryset.exists():
            raise ValidationError(
                {
                    "version": (
                        "A curriculum with this program, academic_year, study_year, "
                        "semester and version already exists."
                    )
                }
            )

    @staticmethod
    def validate_missing_required_units(*, curriculum: Curriculum) -> None:
        if not CurriculumUnit.objects.filter(curriculum=curriculum, is_core=True).exists():
            raise ValidationError(
                {
                    "curriculum_units": (
                        "At least one core unit is required for a curriculum structure."
                    )
                }
            )