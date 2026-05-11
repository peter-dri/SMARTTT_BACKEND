from django.db import models
from django.utils import timezone
from apps.programs.models import Program
from apps.units.models import Unit
from django.conf import settings


class Curriculum(models.Model):
    STATUS_CHOICES = (("active", "Active"), ("inactive", "Inactive"))

    program = models.ForeignKey(Program, related_name="curriculums", on_delete=models.CASCADE)
    academic_year = models.CharField(max_length=64)
    study_year = models.PositiveSmallIntegerField()
    semester = models.PositiveSmallIntegerField()
    version = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="active")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = (("program", "academic_year", "study_year", "semester", "version"),)
        indexes = [models.Index(fields=["program", "academic_year", "study_year", "semester"])]

    def __str__(self):
        return f"{self.program} - Y{self.study_year} S{self.semester} ({self.academic_year}) v{self.version}"


class CurriculumUnit(models.Model):
    curriculum = models.ForeignKey(Curriculum, related_name="units", on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, related_name="curriculum_links", on_delete=models.CASCADE)
    is_core = models.BooleanField(default=True)
    is_elective = models.BooleanField(default=False)
    display_order = models.PositiveSmallIntegerField(default=0)
    prerequisite_unit = models.ForeignKey(Unit, null=True, blank=True, related_name="prerequisite_for", on_delete=models.SET_NULL)
    credit_hours = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)

    class Meta:
        unique_together = (("curriculum", "unit"),)
        ordering = ["display_order"]

    def __str__(self):
        return f"{self.curriculum} -> {self.unit}"
