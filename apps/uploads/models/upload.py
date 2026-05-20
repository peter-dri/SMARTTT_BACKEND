from django.db import models
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _

from apps.common.models import BaseModel

from apps.uploads.utils.constants import DEFAULT_UPLOAD_TYPE, SUPPORTED_UPLOAD_EXTENSIONS


class TimetableUpload(BaseModel):
    class UploadType(models.TextChoices):
        TIMETABLE = "timetable", _("Timetable")

    class ProcessingStatus(models.TextChoices):
        RECEIVED = "received", _("Received")
        VALIDATING = "validating", _("Validating")
        PROCESSING = "processing", _("Processing")
        PARTIAL = "partial", _("Partial")
        PROCESSED = "processed", _("Processed")
        FAILED = "failed", _("Failed")

    uploaded_file = models.FileField(
        upload_to="uploads/timetables/%Y/%m/%d",
        validators=[FileExtensionValidator(allowed_extensions=[ext.lstrip(".") for ext in SUPPORTED_UPLOAD_EXTENSIONS])],
    )
    uploaded_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.PROTECT,
        related_name="timetable_uploads",
    )
    department = models.ForeignKey(
        "departments.Department",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="timetable_uploads",
    )
    program = models.ForeignKey(
        "programs.Program",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="timetable_uploads",
    )
    upload_type = models.CharField(
        max_length=20,
        choices=UploadType.choices,
        default=DEFAULT_UPLOAD_TYPE,
    )
    original_filename = models.CharField(max_length=255)
    processing_status = models.CharField(
        max_length=20,
        choices=ProcessingStatus.choices,
        default=ProcessingStatus.RECEIVED,
    )
    total_rows = models.PositiveIntegerField(default=0)
    successful_rows = models.PositiveIntegerField(default=0)
    failed_rows = models.PositiveIntegerField(default=0)
    error_summary = models.JSONField(default=dict, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "timetable_upload"
        ordering = ["-uploaded_at"]
        indexes = [
            models.Index(fields=["uploaded_by", "uploaded_at"], name="idx_upload_user_date"),
            models.Index(fields=["processing_status", "uploaded_at"], name="idx_upload_status_date"),
            models.Index(fields=["department", "uploaded_at"], name="idx_upload_department_date"),
            models.Index(fields=["program", "uploaded_at"], name="idx_upload_program_date"),
        ]

    def __str__(self) -> str:
        return f"{self.original_filename} ({self.processing_status})"


class UploadProcessingLog(BaseModel):
    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        VALIDATED = "validated", _("Validated")
        SUCCESS = "success", _("Success")
        FAILED = "failed", _("Failed")
        SKIPPED = "skipped", _("Skipped")

    upload = models.ForeignKey(
        TimetableUpload,
        on_delete=models.CASCADE,
        related_name="processing_logs",
    )
    row_number = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    error_message = models.TextField(blank=True)
    raw_data = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "timetable_upload_processing_log"
        ordering = ["row_number", "created_at"]
        indexes = [
            models.Index(fields=["upload", "row_number"], name="idx_upload_log_row"),
            models.Index(fields=["upload", "status"], name="idx_upload_log_status"),
        ]

    def __str__(self) -> str:
        return f"Upload {self.upload_id} row {self.row_number} ({self.status})"


class UploadConflictReport(BaseModel):
    class ConflictType(models.TextChoices):
        ROOM = "room", _("Room Conflict")
        LECTURER = "lecturer", _("Lecturer Conflict")
        OVERLAP = "overlap", _("Overlapping Session")
        DUPLICATE = "duplicate", _("Duplicate Session")
        MAPPING = "mapping", _("Mapping Conflict")

    class Severity(models.TextChoices):
        LOW = "low", _("Low")
        MEDIUM = "medium", _("Medium")
        HIGH = "high", _("High")
        CRITICAL = "critical", _("Critical")

    upload = models.ForeignKey(
        TimetableUpload,
        on_delete=models.CASCADE,
        related_name="conflict_reports",
    )
    conflict_type = models.CharField(max_length=20, choices=ConflictType.choices)
    affected_unit = models.ForeignKey(
        "units.Unit",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="upload_conflict_reports",
    )
    affected_room = models.ForeignKey(
        "rooms.Room",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="upload_conflict_reports",
    )
    affected_lecturer = models.ForeignKey(
        "lecturers.Lecturer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="upload_conflict_reports",
    )
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=Severity.choices, default=Severity.MEDIUM)

    class Meta:
        db_table = "timetable_upload_conflict_report"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["upload", "conflict_type"], name="idx_upload_conflict_type"),
            models.Index(fields=["upload", "severity"], name="idx_upload_conflict_severity"),
        ]

    def __str__(self) -> str:
        return f"{self.upload_id} - {self.conflict_type}"
