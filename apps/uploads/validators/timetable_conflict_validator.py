from __future__ import annotations

from django.db.models import Q

from apps.timetable.models import TimetableSession


class TimetableConflictValidator:
    @staticmethod
    def overlapping_sessions(*, day_of_week: str, start_time, end_time, academic_year: str, semester: int, exclude_session_id: str | None = None):
        queryset = TimetableSession.objects.select_related("room", "lecturer", "time_slot", "unit")
        queryset = queryset.filter(
            day_of_week=day_of_week,
            academic_year=academic_year,
            semester=semester,
        ).filter(
            Q(time_slot__start_time__lt=end_time) & Q(time_slot__end_time__gt=start_time)
        )
        if exclude_session_id:
            queryset = queryset.exclude(id=exclude_session_id)
        return queryset

    @staticmethod
    def room_conflicts(*, room_id: str, day_of_week: str, start_time, end_time, academic_year: str, semester: int):
        return TimetableConflictValidator.overlapping_sessions(
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
            academic_year=academic_year,
            semester=semester,
        ).filter(room_id=room_id)

    @staticmethod
    def lecturer_conflicts(*, lecturer_id: str, day_of_week: str, start_time, end_time, academic_year: str, semester: int):
        return TimetableConflictValidator.overlapping_sessions(
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
            academic_year=academic_year,
            semester=semester,
        ).filter(lecturer_id=lecturer_id)

    @staticmethod
    def duplicate_sessions(*, unit_id: str, program_id: str, study_year: int, semester: int, day_of_week: str, start_time, end_time, academic_year: str, student_group: str):
        return TimetableSession.objects.filter(
            unit_id=unit_id,
            program_id=program_id,
            study_year=study_year,
            semester=semester,
            day_of_week=day_of_week,
            academic_year=academic_year,
            student_group=student_group,
            time_slot__start_time=start_time,
            time_slot__end_time=end_time,
        )