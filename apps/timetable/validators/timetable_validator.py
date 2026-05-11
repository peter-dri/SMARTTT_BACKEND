from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import datetime

from apps.timetable.models import TimetableSession, Room, TimeSlot


class TimetableSessionValidator:
    """
    Validator for timetable session business rules.

    Prevents invalid session configurations:
    - Room conflicts (double-booking)
    - Lecturer conflicts (schedule overlap)
    - Duplicate session creation
    - Invalid scheduling parameters
    """

    @staticmethod
    def validate_session_uniqueness(
        unit_id: str,
        program_id: str,
        study_year: int,
        semester: int,
        day_of_week: str,
        time_slot_id: str,
        student_group: str,
        academic_year: str,
        instance_id: str = None,
    ) -> None:
        """
        Check if an identical session already exists.

        A session is considered duplicate if it has the same:
        - Unit, Program, Study Year, Semester, Day, TimeSlot, StudentGroup, AcademicYear

        Args:
            unit_id: Unit ID
            program_id: Program ID
            study_year: Academic year of study (1-5)
            semester: Semester (1 or 2)
            day_of_week: Day of week
            time_slot_id: Time slot ID
            student_group: Student group identifier
            academic_year: Academic year
            instance_id: Instance ID for updates (to exclude from check)

        Raises:
            ValidationError: If duplicate session found
        """
        query = TimetableSession.objects.filter(
            unit_id=unit_id,
            program_id=program_id,
            study_year=study_year,
            semester=semester,
            day_of_week=day_of_week,
            time_slot_id=time_slot_id,
            student_group=student_group,
            academic_year=academic_year,
        )

        if instance_id:
            query = query.exclude(id=instance_id)

        if query.exists():
            raise ValidationError(
                _("A session with these exact parameters already exists"),
                code="duplicate_session",
            )

    @staticmethod
    def validate_room_conflict(
        room_id: str,
        day_of_week: str,
        time_slot_id: str,
        academic_year: str,
        semester: int,
        instance_id: str = None,
    ) -> None:
        """
        Check if room is already booked at the given time.

        Args:
            room_id: Room ID
            day_of_week: Day of week
            time_slot_id: Time slot ID
            academic_year: Academic year
            semester: Semester
            instance_id: Instance ID for updates (to exclude from check)

        Raises:
            ValidationError: If room conflict detected
        """
        if not room_id:
            return  # No room to check

        query = TimetableSession.objects.filter(
            room_id=room_id,
            day_of_week=day_of_week,
            time_slot_id=time_slot_id,
            academic_year=academic_year,
            semester=semester,
            status__in=["scheduled", "active"],
        )

        if instance_id:
            query = query.exclude(id=instance_id)

        if query.exists():
            room = Room.objects.get(id=room_id)
            raise ValidationError(
                _(f"Room {room.code} is already booked for this time slot"),
                code="room_conflict",
            )

    @staticmethod
    def validate_lecturer_conflict(
        lecturer_id: str,
        day_of_week: str,
        time_slot_id: str,
        academic_year: str,
        semester: int,
        instance_id: str = None,
    ) -> None:
        """
        Check if lecturer is already assigned to another session at the same time.

        Args:
            lecturer_id: Lecturer ID
            day_of_week: Day of week
            time_slot_id: Time slot ID
            academic_year: Academic year
            semester: Semester
            instance_id: Instance ID for updates (to exclude from check)

        Raises:
            ValidationError: If lecturer conflict detected
        """
        if not lecturer_id:
            return  # No lecturer to check

        query = TimetableSession.objects.filter(
            lecturer_id=lecturer_id,
            day_of_week=day_of_week,
            time_slot_id=time_slot_id,
            academic_year=academic_year,
            semester=semester,
            status__in=["scheduled", "active"],
        )

        if instance_id:
            query = query.exclude(id=instance_id)

        if query.exists():
            raise ValidationError(
                _("Lecturer is already assigned to another session at this time"),
                code="lecturer_conflict",
            )

    @staticmethod
    def validate_time_slot_validity(time_slot_id: str) -> None:
        """
        Check if time slot is valid and active.

        Args:
            time_slot_id: Time slot ID

        Raises:
            ValidationError: If time slot is invalid or inactive
        """
        try:
            time_slot = TimeSlot.objects.get(id=time_slot_id)
        except TimeSlot.DoesNotExist:
            raise ValidationError(
                _("Selected time slot does not exist"),
                code="invalid_time_slot",
            )

        if not time_slot.is_active():
            raise ValidationError(
                _("Selected time slot is no longer active"),
                code="inactive_time_slot",
            )

    @staticmethod
    def validate_room_capacity(room_id: str, max_students: int) -> None:
        """
        Check if max students exceeds room capacity.

        Args:
            room_id: Room ID
            max_students: Planned number of students

        Raises:
            ValidationError: If max_students exceeds room capacity
        """
        if not room_id:
            return

        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            raise ValidationError(
                _("Selected room does not exist"),
                code="invalid_room",
            )

        if max_students > room.capacity:
            raise ValidationError(
                _(f"Max students ({max_students}) exceeds room capacity ({room.capacity})"),
                code="exceeds_room_capacity",
            )

        if not room.is_available():
            raise ValidationError(
                _(f"Room {room.code} is not available for scheduling"),
                code="room_unavailable",
            )

    @staticmethod
    def validate_semester(semester: int) -> None:
        """Validate semester value."""
        if semester not in [1, 2]:
            raise ValidationError(
                _("Semester must be 1 or 2"),
                code="invalid_semester",
            )

    @staticmethod
    def validate_study_year(study_year: int) -> None:
        """Validate study year."""
        if not (1 <= study_year <= 5):
            raise ValidationError(
                _("Study year must be between 1 and 5"),
                code="invalid_study_year",
            )

    @staticmethod
    def validate_academic_year_format(academic_year: str) -> None:
        """
        Validate academic year format.

        Expected format: YYYY/YYYY (e.g., 2024/2025)

        Args:
            academic_year: Academic year string

        Raises:
            ValidationError: If format is invalid
        """
        if not academic_year or "/" not in academic_year:
            raise ValidationError(
                _("Academic year format must be YYYY/YYYY (e.g., 2024/2025)"),
                code="invalid_academic_year_format",
            )

        try:
            parts = academic_year.split("/")
            if len(parts) != 2:
                raise ValueError

            start_year = int(parts[0])
            end_year = int(parts[1])

            if end_year != start_year + 1:
                raise ValueError

            current_year = datetime.now().year
            if start_year < current_year - 5 or start_year > current_year + 5:
                raise ValueError

        except (ValueError, IndexError):
            raise ValidationError(
                _("Invalid academic year. Format: YYYY/YYYY"),
                code="invalid_academic_year_value",
            )

    @staticmethod
    def validate_max_students(max_students: int) -> None:
        """Validate maximum students value."""
        if max_students <= 0:
            raise ValidationError(
                _("Maximum students must be greater than 0"),
                code="invalid_max_students",
            )

        if max_students > 500:
            raise ValidationError(
                _("Maximum students cannot exceed 500"),
                code="max_students_too_high",
            )


class ConflictValidator:
    """
    Validator for detecting various types of scheduling conflicts.

    Detects:
    - Room conflicts
    - Lecturer conflicts
    - Time overlaps
    """

    @staticmethod
    def check_for_conflicts(
        day_of_week: str,
        time_slot_id: str,
        room_id: str = None,
        lecturer_id: str = None,
        academic_year: str = None,
        semester: int = None,
        instance_id: str = None,
    ) -> list:
        """
        Comprehensive conflict check.

        Returns all detected conflicts.

        Args:
            day_of_week: Day of week
            time_slot_id: Time slot ID
            room_id: Room ID (optional)
            lecturer_id: Lecturer ID (optional)
            academic_year: Academic year
            semester: Semester
            instance_id: Instance ID to exclude

        Returns:
            List of conflict dictionaries with type and affected session info
        """
        conflicts = []

        # Check room conflicts
        if room_id:
            query = TimetableSession.objects.filter(
                room_id=room_id,
                day_of_week=day_of_week,
                time_slot_id=time_slot_id,
                academic_year=academic_year,
                semester=semester,
                status__in=["scheduled", "active"],
            )

            if instance_id:
                query = query.exclude(id=instance_id)

            for session in query:
                conflicts.append(
                    {
                        "type": "room_conflict",
                        "message": f"Room conflict with {session.unit.code}",
                        "conflicting_session_id": str(session.id),
                    }
                )

        # Check lecturer conflicts
        if lecturer_id:
            query = TimetableSession.objects.filter(
                lecturer_id=lecturer_id,
                day_of_week=day_of_week,
                time_slot_id=time_slot_id,
                academic_year=academic_year,
                semester=semester,
                status__in=["scheduled", "active"],
            )

            if instance_id:
                query = query.exclude(id=instance_id)

            for session in query:
                conflicts.append(
                    {
                        "type": "lecturer_conflict",
                        "message": f"Lecturer already assigned to {session.unit.code}",
                        "conflicting_session_id": str(session.id),
                    }
                )

        return conflicts
