from django.db import models
from django.utils import timezone
from apps.departments.models import Department


class Unit(models.Model):
    STATUS_CHOICES = (("active", "Active"), ("inactive", "Inactive"))

    code = models.CharField(max_length=64)
    name = models.CharField(max_length=255)
    credit_hours = models.DecimalField(max_digits=4, decimal_places=1)
    description = models.TextField(blank=True)
    department = models.ForeignKey(Department, related_name="units", on_delete=models.CASCADE)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="active")

    class Meta:
        unique_together = (("department", "code"), ("department", "name"))
        indexes = [models.Index(fields=["department", "code"])]

    def __str__(self):
        return f"{self.name} ({self.code})"
