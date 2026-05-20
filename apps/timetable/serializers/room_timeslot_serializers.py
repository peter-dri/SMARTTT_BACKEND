from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from apps.timetable.models import Room, TimeSlot, TimetableSession
from apps.units.models import Unit
from apps.lecturers.models import Lecturer


class RoomListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing rooms."""

    room_type_display = serializers.CharField(
        source="get_room_type_display",
        read_only=True,
    )
    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )
    is_available = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Room
        fields = [
            "id",
            "name",
            "code",
            "building",
            "floor",
            "capacity",
            "room_type",
            "room_type_display",
            "status",
            "status_display",
            "is_available",
        ]

    def get_is_available(self, obj) -> bool:
        """Check if room is available for scheduling."""
        return obj.is_available()


class RoomDetailSerializer(serializers.ModelSerializer):
    """Full detail serializer for room."""

    room_type_display = serializers.CharField(
        source="get_room_type_display",
        read_only=True,
    )
    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )
    is_available = serializers.SerializerMethodField(read_only=True)
    type_short = serializers.SerializerMethodField(read_only=True)
    sessions_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Room
        fields = [
            "id",
            "name",
            "code",
            "building",
            "floor",
            "capacity",
            "room_type",
            "room_type_display",
            "type_short",
            "status",
            "status_display",
            "description",
            "facilities",
            "is_available",
            "sessions_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_is_available(self, obj) -> bool:
        return obj.is_available()

    def get_type_short(self, obj) -> str:
        return obj.get_type_display_short()

    def get_sessions_count(self, obj) -> int:
        """Get count of timetable sessions in this room."""
        return obj.timetable_sessions.filter(status="scheduled").count()


class RoomCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for room creation and updates."""

    class Meta:
        model = Room
        fields = [
            "name",
            "code",
            "building",
            "floor",
            "capacity",
            "room_type",
            "status",
            "description",
            "facilities",
        ]

    def validate_capacity(self, value):
        """Validate room capacity."""
        if value <= 0:
            raise serializers.ValidationError(_("Capacity must be greater than 0"))
        if value > 500:
            raise serializers.ValidationError(_("Capacity cannot exceed 500"))
        return value

    def validate_floor(self, value):
        """Validate floor number."""
        if value < 0:
            raise serializers.ValidationError(_("Floor number cannot be negative"))
        if value > 50:
            raise serializers.ValidationError(_("Floor number seems unrealistic (>50)"))
        return value

    def validate_code(self, value):
        """Validate room code is unique."""
        if self.instance and Room.objects.filter(code=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError(_("Room code must be unique"))
        return value.upper()


class TimeSlotListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing time slots."""

    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )
    time_range = serializers.SerializerMethodField(read_only=True)
    is_active = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TimeSlot
        fields = [
            "id",
            "slot_name",
            "start_time",
            "end_time",
            "time_range",
            "duration_minutes",
            "status",
            "status_display",
            "is_active",
        ]

    def get_time_range(self, obj) -> str:
        """Get formatted time range."""
        start = obj.start_time.strftime("%H:%M")
        end = obj.end_time.strftime("%H:%M")
        return f"{start} - {end}"

    def get_is_active(self, obj) -> bool:
        return obj.is_active()


class TimeSlotDetailSerializer(serializers.ModelSerializer):
    """Full detail serializer for time slot."""

    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )
    time_range = serializers.SerializerMethodField(read_only=True)
    is_active = serializers.SerializerMethodField(read_only=True)
    sessions_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TimeSlot
        fields = [
            "id",
            "slot_name",
            "start_time",
            "end_time",
            "time_range",
            "duration_minutes",
            "status",
            "status_display",
            "description",
            "is_active",
            "sessions_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "duration_minutes", "created_at", "updated_at"]

    def get_time_range(self, obj) -> str:
        start = obj.start_time.strftime("%H:%M")
        end = obj.end_time.strftime("%H:%M")
        return f"{start} - {end}"

    def get_is_active(self, obj) -> bool:
        return obj.is_active()

    def get_sessions_count(self, obj) -> int:
        """Get count of timetable sessions using this slot."""
        return obj.timetable_sessions.filter(status="scheduled").count()


class TimeSlotCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for time slot creation and updates."""

    class Meta:
        model = TimeSlot
        fields = [
            "slot_name",
            "start_time",
            "end_time",
            "status",
            "description",
        ]

    def validate(self, data):
        """Cross-field validation."""
        start_time = data.get("start_time")
        end_time = data.get("end_time")

        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError(
                {
                    "end_time": _("End time must be after start time"),
                }
            )

        return data

    def validate_slot_name(self, value):
        """Validate slot name."""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError(_("Slot name cannot be empty"))
        return value
