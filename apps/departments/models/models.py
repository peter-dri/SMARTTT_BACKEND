from django.db import models
from django.conf import settings
from django.utils import timezone


class Faculty(models.Model):
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=32, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Faculty"
        verbose_name_plural = "Faculties"

    def __str__(self):
        return f"{self.name} ({self.code})"


class Department(models.Model):
    STATUS_CHOICES = (("active", "Active"), ("inactive", "Inactive"))

    faculty = models.ForeignKey(Faculty, related_name="departments", on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=32)
    description = models.TextField(blank=True)
    head_of_department = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="headed_departments")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="active")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = (("faculty", "code"),)
        indexes = [models.Index(fields=["faculty", "code"])]
        ordering = ["faculty", "name"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class DepartmentAdmin(models.Model):
    ROLE_CHOICES = (("admin", "Admin"), ("editor", "Editor"))

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="department_assignments", on_delete=models.CASCADE)
    department = models.ForeignKey(Department, related_name="admins", on_delete=models.CASCADE)
    role = models.CharField(max_length=32, choices=ROLE_CHOICES, default="admin")
    assigned_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = (("user", "department"),)
        indexes = [models.Index(fields=["department"])]

    def __str__(self):
        return f"{self.user} -> {self.department} ({self.role})"
