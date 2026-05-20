from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from apps.common.models import BaseModel


class Curriculum(BaseModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"

    program = models.ForeignKey(
        "programs.Program",
        on_delete=models.PROTECT,
        related_name="curricula",
    )
    department = models.ForeignKey(
        "departments.Department",
        on_delete=models.PROTECT,
        related_name="curricula",
    )
    academic_year = models.CharField(max_length=20)
    study_year = models.PositiveSmallIntegerField()
    semester = models.PositiveSmallIntegerField()
    version = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_curricula",
    )

    class Meta:
        ordering = [
            "program__code",
            "academic_year",
            "study_year",
            "semester",
            "-version",
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["program", "academic_year", "study_year", "semester", "version"],
                name="uq_curriculum_program_term_version",
            ),
            models.UniqueConstraint(
                fields=["program", "academic_year", "study_year", "semester"],
                condition=Q(status="active"),
                name="uq_curriculum_single_active_per_term",
            ),
        ]
        indexes = [
            models.Index(fields=["department", "status"], name="idx_curriculum_dept_status"),
            models.Index(fields=["program", "study_year", "semester"], name="idx_curriculum_program_y_s"),
        ]

    def clean(self) -> None:
        if self.program_id and self.department_id and self.program.department_id != self.department_id:
            raise ValidationError("Curriculum department must match the program department.")

        if self.semester not in (1, 2, 3):
            raise ValidationError("semester must be 1, 2, or 3.")

        if self.study_year < 1:
            raise ValidationError("study_year must be greater than or equal to 1.")

        if self.program_id and self.study_year > self.program.duration_years:
            raise ValidationError("study_year exceeds the program duration.")

    def __str__(self) -> str:
        return (
            f"{self.program.code} {self.academic_year} "
            f"Y{self.study_year} S{self.semester} v{self.version}"
        )


class CurriculumVersion(BaseModel):
    class Action(models.TextChoices):
        CREATED = "created", "Created"
        ACTIVATED = "activated", "Activated"
        DEACTIVATED = "deactivated", "Deactivated"
        UPDATED = "updated", "Updated"

    curriculum = models.ForeignKey(
        "curriculum.Curriculum",
        on_delete=models.CASCADE,
        related_name="version_history",
    )
    version = models.PositiveIntegerField()
    action = models.CharField(max_length=20, choices=Action.choices)
    change_summary = models.TextField(blank=True)
    acted_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="curriculum_version_actions",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["curriculum", "version"], name="idx_curriculum_version_lookup"),
        ]


class CurriculumUnit(BaseModel):
    curriculum = models.ForeignKey(
        "curriculum.Curriculum",
        on_delete=models.CASCADE,
        related_name="curriculum_units",
    )
    unit = models.ForeignKey(
        "units.Unit",
        on_delete=models.PROTECT,
        related_name="curriculum_mappings",
    )
    is_core = models.BooleanField(default=True)
    is_elective = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=1)
    prerequisite_unit = models.ForeignKey(
        "units.Unit",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="dependent_curriculum_units",
    )
    credit_hours = models.PositiveSmallIntegerField(default=3)

    class Meta:
        ordering = ["curriculum", "display_order", "unit__code"]
        constraints = [
            models.UniqueConstraint(
                fields=["curriculum", "unit"],
                name="uq_curriculumunit_curriculum_unit",
            ),
        ]
        indexes = [
            models.Index(fields=["curriculum", "display_order"], name="idx_curriculumunit_order"),
            models.Index(fields=["unit"], name="idx_curriculumunit_unit"),
        ]

    def clean(self) -> None:
        if self.is_core and self.is_elective:
            raise ValidationError("A curriculum unit cannot be both core and elective.")

        if not self.is_core and not self.is_elective:
            raise ValidationError("A curriculum unit must be core or elective.")

        if self.prerequisite_unit_id and self.prerequisite_unit_id == self.unit_id:
            raise ValidationError("A unit cannot be a prerequisite of itself.")

        if self.credit_hours < 1:
            raise ValidationError("credit_hours must be greater than 0.")

    def __str__(self) -> str:
        return f"{self.curriculum} / {self.unit.code}"
