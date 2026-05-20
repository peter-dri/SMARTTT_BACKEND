from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.common.models import BaseModel


class TimeSlot(BaseModel):
    """
    Model representing standard time slots used in timetable scheduling.

    Time slots define when classes occur within a day.
    They are reusable across multiple timetable sessions.

    Examples:
    - 8:00 AM - 10:00 AM
    - 10:00 AM - 12:00 PM
    - 2:00 PM - 4:00 PM
    """

    class Status(models.TextChoices):
        """Time slot operational status."""

        ACTIVE = "active", _("Active")
        INACTIVE = "inactive", _("Inactive")
        ARCHIVED = "archived", _("Archived")

    # Core fields
    start_time = models.TimeField(
        help_text=_("Session start time (e.g., 08:00)"),
    )
    end_time = models.TimeField(
        help_text=_("Session end time (e.g., 10:00)"),
    )
    slot_name = models.CharField(
        max_length=255,
        help_text=_("Descriptive name (e.g., Morning Slot 1, Afternoon Session)"),
    )
    duration_minutes = models.PositiveSmallIntegerField(
        help_text=_("Duration of slot in minutes"),
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        help_text=_("Current operational status"),
    )

    # Additional info
    description = models.TextField(
        blank=True,
        help_text=_("Additional details about this time slot"),
    )

    class Meta:
        db_table = "timetable_timeslot"
        indexes = [
            models.Index(fields=["start_time"]),
            models.Index(fields=["status"]),
        ]
        ordering = ["start_time"]
        verbose_name = _("Time Slot")
        verbose_name_plural = _("Time Slots")
        unique_together = ["start_time", "end_time"]

    def __str__(self) -> str:
        return f"{self.slot_name} ({self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')})"

    def clean(self):
        """Model-level validation."""
        if self.start_time >= self.end_time:
            raise ValidationError(
                _("Start time must be before end time"),
                code="invalid_times",
            )

        # Calculate duration
        from datetime import datetime, timedelta

        start = datetime.combine(datetime.today(), self.start_time)
        end = datetime.combine(datetime.today(), self.end_time)
        duration = int((end - start).total_seconds() / 60)

        if self.duration_minutes != duration:
            raise ValidationError(
                _(f"Duration must be {duration} minutes for the given times"),
                code="invalid_duration",
            )

    def save(self, *args, **kwargs):
        """Auto-calculate duration before saving."""
        if not self.duration_minutes:
            from datetime import datetime

            start = datetime.combine(datetime.today(), self.start_time)
            end = datetime.combine(datetime.today(), self.end_time)
            self.duration_minutes = int((end - start).total_seconds() / 60)

        self.full_clean()
        super().save(*args, **kwargs)

    def is_active(self) -> bool:
        """Check if time slot is active."""
        return self.status == self.Status.ACTIVE

    def overlaps_with(self, other: "TimeSlot") -> bool:
        """
        Check if this time slot overlaps with another.

        Args:
            other: Another TimeSlot instance to check overlap

        Returns:
            True if slots overlap, False otherwise
        """
        return not (self.end_time <= other.start_time or self.start_time >= other.end_time)
