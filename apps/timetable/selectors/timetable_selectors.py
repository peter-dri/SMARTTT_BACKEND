"""
Timetable selector layer for optimized database queries.

Encapsulates reusable query logic:
- Prevents N+1 queries with select_related/prefetch_related
- Provides consistent interface for complex queries
- Centralizes database query optimization
"""

from django.db.models import Q, F, Count, Prefetch
from django.db.models.functions import Cast
from django.db import models

from apps.timetable.models import TimetableSession, Room, TimeSlot


class TimetableSessionSelector:
    """
    Optimized queries for timetable sessions.

    Prevents N+1 queries by using select_related and prefetch_related.
    """

    @staticmethod
    def get_base_queryset() -> models.QuerySet:
        """
        Get base queryset with optimal prefetching.

        Includes: Unit, Program, Department, Lecturer, Room, TimeSlot
        """
        return TimetableSession.objects.select_related(
            "unit",
            "unit__department",
            "program",
            "department",
            "lecturer",
            "lecturer__user",
            "lecturer__department",
            "room",
            "time_slot",
            "created_by",
        ).prefetch_related()

    @staticmethod
    def get_session_by_id(session_id: str) -> TimetableSession:
        """Get single session with all relationships."""
        return TimetableSessionSelector.get_base_queryset().get(id=session_id)

    @staticmethod
    def get_all_sessions(
        academic_year: str = None,
        semester: int = None,
        status: str = None,
    ) -> models.QuerySet:
        """
        Get all sessions with optional filters.

        Args:
            academic_year: Filter by academic year
            semester: Filter by semester (1 or 2)
            status: Filter by status

        Returns:
            Optimized queryset
        """
        queryset = TimetableSessionSelector.get_base_queryset()

        if academic_year:
            queryset = queryset.filter(academic_year=academic_year)

        if semester:
            queryset = queryset.filter(semester=semester)

        if status:
            queryset = queryset.filter(status=status)

        return queryset.order_by("day_of_week", "time_slot__start_time")

    @staticmethod
    def get_sessions_by_program(
        program_id: str,
        academic_year: str,
        study_year: int,
        semester: int,
    ) -> models.QuerySet:
        """
        Get sessions for a specific program/year/semester.

        Used for student timetable filtering.

        Args:
            program_id: Program ID
            academic_year: Academic year
            study_year: Year of study (1-5)
            semester: Semester (1 or 2)

        Returns:
            Optimized queryset of sessions
        """
        return (
            TimetableSessionSelector.get_base_queryset()
            .filter(
                program_id=program_id,
                academic_year=academic_year,
                study_year=study_year,
                semester=semester,
                status__in=["scheduled", "active"],
            )
            .order_by("day_of_week", "time_slot__start_time")
        )

    @staticmethod
    def get_sessions_by_department(
        department_id: str,
        academic_year: str = None,
        semester: int = None,
    ) -> models.QuerySet:
        """
        Get all sessions for a department.

        Used by department admins.

        Args:
            department_id: Department ID
            academic_year: Optional academic year filter
            semester: Optional semester filter

        Returns:
            Optimized queryset
        """
        queryset = TimetableSessionSelector.get_base_queryset().filter(
            department_id=department_id
        )

        if academic_year:
            queryset = queryset.filter(academic_year=academic_year)

        if semester:
            queryset = queryset.filter(semester=semester)

        return queryset.order_by("day_of_week", "time_slot__start_time")

    @staticmethod
    def get_sessions_by_lecturer(
        lecturer_id: str,
        academic_year: str = None,
        semester: int = None,
    ) -> models.QuerySet:
        """
        Get sessions assigned to a lecturer.

        Args:
            lecturer_id: Lecturer ID
            academic_year: Optional academic year filter
            semester: Optional semester filter

        Returns:
            Optimized queryset
        """
        queryset = TimetableSessionSelector.get_base_queryset().filter(
            lecturer_id=lecturer_id
        )

        if academic_year:
            queryset = queryset.filter(academic_year=academic_year)

        if semester:
            queryset = queryset.filter(semester=semester)

        return queryset.order_by("day_of_week", "time_slot__start_time")

    @staticmethod
    def get_sessions_by_room(
        room_id: str,
        day_of_week: str = None,
        academic_year: str = None,
    ) -> models.QuerySet:
        """
        Get sessions scheduled in a room.

        Args:
            room_id: Room ID
            day_of_week: Optional day filter
            academic_year: Optional academic year filter

        Returns:
            Optimized queryset
        """
        queryset = TimetableSessionSelector.get_base_queryset().filter(room_id=room_id)

        if day_of_week:
            queryset = queryset.filter(day_of_week=day_of_week)

        if academic_year:
            queryset = queryset.filter(academic_year=academic_year)

        return queryset.order_by("day_of_week", "time_slot__start_time")

    @staticmethod
    def get_sessions_by_day_and_slot(
        day_of_week: str,
        time_slot_id: str,
        academic_year: str,
        semester: int,
    ) -> models.QuerySet:
        """
        Get all sessions at a specific day/time (for conflict detection).

        Args:
            day_of_week: Day of week
            time_slot_id: Time slot ID
            academic_year: Academic year
            semester: Semester

        Returns:
            Queryset of overlapping sessions
        """
        return TimetableSessionSelector.get_base_queryset().filter(
            day_of_week=day_of_week,
            time_slot_id=time_slot_id,
            academic_year=academic_year,
            semester=semester,
            status__in=["scheduled", "active"],
        )

    @staticmethod
    def get_sessions_for_unit(
        unit_id: str,
        academic_year: str = None,
    ) -> models.QuerySet:
        """
        Get all sessions for a specific unit.

        Args:
            unit_id: Unit ID
            academic_year: Optional academic year filter

        Returns:
            Optimized queryset
        """
        queryset = TimetableSessionSelector.get_base_queryset().filter(unit_id=unit_id)

        if academic_year:
            queryset = queryset.filter(academic_year=academic_year)

        return queryset.order_by("program", "study_year", "semester", "day_of_week")

    @staticmethod
    def get_active_sessions(
        academic_year: str = None,
        semester: int = None,
    ) -> models.QuerySet:
        """
        Get currently active sessions (scheduled or active status).

        Args:
            academic_year: Optional academic year filter
            semester: Optional semester filter

        Returns:
            Optimized queryset
        """
        queryset = TimetableSessionSelector.get_base_queryset().filter(
            status__in=["scheduled", "active"]
        )

        if academic_year:
            queryset = queryset.filter(academic_year=academic_year)

        if semester:
            queryset = queryset.filter(semester=semester)

        return queryset

    @staticmethod
    def get_sessions_with_enrollment_counts(
        academic_year: str = None,
        semester: int = None,
    ) -> models.QuerySet:
        """
        Get sessions with additional enrollment statistics.

        Adds annotations for occupancy calculations.

        Args:
            academic_year: Optional academic year filter
            semester: Optional semester filter

        Returns:
            Annotated queryset with enrollment_percentage
        """
        queryset = (
            TimetableSessionSelector.get_base_queryset()
            .annotate(
                enrollment_percentage=Cast(
                    F("current_enrollment") * 100 / F("max_students"),
                    models.FloatField(),
                )
            )
            .filter(status__in=["scheduled", "active"])
        )

        if academic_year:
            queryset = queryset.filter(academic_year=academic_year)

        if semester:
            queryset = queryset.filter(semester=semester)

        return queryset

    @staticmethod
    def get_conflicting_sessions(
        day_of_week: str,
        time_slot_id: str,
        room_id: str = None,
        lecturer_id: str = None,
        academic_year: str = None,
        semester: int = None,
    ) -> models.QuerySet:
        """
        Get conflicting sessions (room or lecturer overlaps).

        Args:
            day_of_week: Day of week
            time_slot_id: Time slot ID
            room_id: Optional room ID for room conflict detection
            lecturer_id: Optional lecturer ID for lecturer conflict detection
            academic_year: Academic year
            semester: Semester

        Returns:
            Queryset of conflicting sessions
        """
        base_filter = Q(
            day_of_week=day_of_week,
            time_slot_id=time_slot_id,
            academic_year=academic_year,
            semester=semester,
            status__in=["scheduled", "active"],
        )

        filters = base_filter

        if room_id:
            filters |= Q(
                **{
                    "room_id": room_id,
                    "day_of_week": day_of_week,
                    "time_slot_id": time_slot_id,
                    "academic_year": academic_year,
                    "semester": semester,
                    "status__in": ["scheduled", "active"],
                }
            )

        if lecturer_id:
            filters |= Q(
                **{
                    "lecturer_id": lecturer_id,
                    "day_of_week": day_of_week,
                    "time_slot_id": time_slot_id,
                    "academic_year": academic_year,
                    "semester": semester,
                    "status__in": ["scheduled", "active"],
                }
            )

        return TimetableSessionSelector.get_base_queryset().filter(filters)


class RoomSelector:
    """Optimized queries for rooms."""

    @staticmethod
    def get_all_available_rooms() -> models.QuerySet:
        """Get all active rooms."""
        return Room.objects.filter(status="active").order_by("building", "code")

    @staticmethod
    def get_room_by_id(room_id: str) -> Room:
        """Get single room by ID."""
        return Room.objects.get(id=room_id)

    @staticmethod
    def get_rooms_by_capacity(min_capacity: int) -> models.QuerySet:
        """Get rooms with at least specified capacity."""
        return Room.objects.filter(
            status="active",
            capacity__gte=min_capacity,
        ).order_by("capacity")

    @staticmethod
    def get_rooms_by_type(room_type: str) -> models.QuerySet:
        """Get rooms by type."""
        return Room.objects.filter(
            status="active",
            room_type=room_type,
        ).order_by("building", "code")

    @staticmethod
    def get_rooms_by_building(building: str) -> models.QuerySet:
        """Get rooms in a building."""
        return Room.objects.filter(
            status="active",
            building=building,
        ).order_by("floor", "code")


class TimeSlotSelector:
    """Optimized queries for time slots."""

    @staticmethod
    def get_all_active_slots() -> models.QuerySet:
        """Get all active time slots."""
        return TimeSlot.objects.filter(status="active").order_by("start_time")

    @staticmethod
    def get_slot_by_id(slot_id: str) -> TimeSlot:
        """Get single time slot by ID."""
        return TimeSlot.objects.get(id=slot_id)

    @staticmethod
    def get_slots_by_time_range(start_time, end_time) -> models.QuerySet:
        """Get time slots within a time range."""
        return (
            TimeSlot.objects.filter(
                status="active",
                start_time__gte=start_time,
                end_time__lte=end_time,
            )
            .order_by("start_time")
        )
