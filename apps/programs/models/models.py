from django.db import models
from django.utils import timezone
from apps.departments.models import Department


class Program(models.Model):
    STATUS_CHOICES = (("active", "Active"), ("inactive", "Inactive"))

    department = models.ForeignKey(Department, related_name="programs", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=64)
    duration_years = models.PositiveSmallIntegerField(default=3)
    award_type = models.CharField(max_length=128, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="active")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = (("department", "code"), ("department", "name"))
        indexes = [models.Index(fields=["department", "code"])]

    def __str__(self):
        return f"{self.name} ({self.code})"
