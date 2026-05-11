from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.common.models import BaseModel


class Room(BaseModel):
    """
    Model representing a physical room/venue where classes are held.

    Rooms can be lecture halls, laboratories, tutorials, etc.
    Each room has capacity constraints and can be tracked for occupancy.
    """

    class RoomType(models.TextChoices):
        """Room type classification."""

        LECTURE_HALL = "lecture_hall", _("Lecture Hall")
        LABORATORY = "laboratory", _("Laboratory")
        TUTORIAL = "tutorial", _("Tutorial Room")
        SEMINAR = "seminar", _("Seminar Room")
        AUDITORIUM = "auditorium", _("Auditorium")
        COMPUTER_LAB = "computer_lab", _("Computer Lab")
        STUDIO = "studio", _("Studio")
        GYMNASIUM = "gymnasium", _("Gymnasium")
        OTHER = "other", _("Other")

    class Status(models.TextChoices):
        """Room operational status."""

        ACTIVE = "active", _("Active")
        MAINTENANCE = "maintenance", _("Under Maintenance")
        CLOSED = "closed", _("Closed")
        UNAVAILABLE = "unavailable", _("Unavailable")

    # Core fields
    name = models.CharField(
        max_length=255,
        help_text=_("Room name (e.g., Lab 1, Room A101)"),
    )
    code = models.CharField(
        max_length=30,
        unique=True,
        help_text=_("Unique room code (e.g., LH-001, LAB-04)"),
    )
    building = models.CharField(
        max_length=255,
        help_text=_("Building name or block where room is located"),
    )
    floor = models.PositiveSmallIntegerField(
        default=1,
        help_text=_("Floor number"),
    )
    capacity = models.PositiveSmallIntegerField(
        help_text=_("Maximum number of students the room can accommodate"),
    )
    room_type = models.CharField(
        max_length=20,
        choices=RoomType.choices,
        default=RoomType.LECTURE_HALL,
        help_text=_("Type of room"),
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        help_text=_("Current operational status"),
    )

    # Additional information
    description = models.TextField(
        blank=True,
        help_text=_("Additional details about the room"),
    )
    facilities = models.JSONField(
        default=list,
        blank=True,
        help_text=_("List of facilities available (e.g., projector, whiteboard, AC)"),
    )

    class Meta:
        db_table = "timetable_room"
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["building"]),
            models.Index(fields=["room_type"]),
            models.Index(fields=["status"]),
            models.Index(fields=["capacity"]),
        ]
        verbose_name = _("Room")
        verbose_name_plural = _("Rooms")
        ordering = ["building", "code"]

    def __str__(self) -> str:
        return f"{self.code} - {self.name} ({self.capacity} capacity)"

    def clean(self):
        """Model-level validation."""
        if self.capacity <= 0:
            raise ValidationError(_("Capacity must be greater than 0"))

        if self.floor < 0:
            raise ValidationError(_("Floor number cannot be negative"))

    def is_available(self) -> bool:
        """Check if room is available for scheduling."""
        return self.status == self.Status.ACTIVE

    def get_type_display_short(self) -> str:
        """Get short display name for room type."""
        type_map = {
            "lecture_hall": "LH",
            "laboratory": "LAB",
            "tutorial": "TUT",
            "seminar": "SEM",
            "auditorium": "AUD",
            "computer_lab": "COMP",
            "studio": "STD",
            "gymnasium": "GYM",
            "other": "OTH",
        }
        return type_map.get(self.room_type, "UNK")
