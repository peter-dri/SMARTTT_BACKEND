from __future__ import annotations

from django.db import transaction

from apps.uploads.models import TimetableUpload, UploadConflictReport
from apps.uploads.validators import TimetableConflictValidator


class UploadConflictService:
    @staticmethod
    @transaction.atomic
    def detect_for_row(*, upload: TimetableUpload, row_number: int, row: dict, mappings: dict) -> list[UploadConflictReport]:
        conflicts: list[UploadConflictReport] = []
        time_slot = mappings["time_slot"]
        if not time_slot:
            return conflicts

        room_conflicts = TimetableConflictValidator.room_conflicts(
            room_id=mappings["room"].id if mappings.get("room") else None,
            day_of_week=row["day"],
            start_time=time_slot.start_time,
            end_time=time_slot.end_time,
            academic_year=row["academic_year"],
            semester=row["semester"],
        ) if mappings.get("room") else []

        lecturer_conflicts = TimetableConflictValidator.lecturer_conflicts(
            lecturer_id=mappings["lecturer"].id if mappings.get("lecturer") else None,
            day_of_week=row["day"],
            start_time=time_slot.start_time,
            end_time=time_slot.end_time,
            academic_year=row["academic_year"],
            semester=row["semester"],
        ) if mappings.get("lecturer") else []

        duplicate_conflicts = TimetableConflictValidator.duplicate_sessions(
            unit_id=mappings["unit"].id if mappings.get("unit") else None,
            program_id=mappings["program"].id if mappings.get("program") else None,
            study_year=row["study_year"],
            semester=row["semester"],
            day_of_week=row["day"],
            start_time=time_slot.start_time,
            end_time=time_slot.end_time,
            academic_year=row["academic_year"],
            student_group=mappings["student_group"],
        ) if mappings.get("unit") and mappings.get("program") else []

        if room_conflicts.exists():
            conflicts.append(UploadConflictReport(
                upload=upload,
                conflict_type=UploadConflictReport.ConflictType.ROOM,
                affected_unit=mappings.get("unit"),
                affected_room=mappings.get("room"),
                affected_lecturer=mappings.get("lecturer"),
                description=f"Row {row_number}: room already booked at this time.",
                severity=UploadConflictReport.Severity.HIGH,
            ))
        if lecturer_conflicts.exists():
            conflicts.append(UploadConflictReport(
                upload=upload,
                conflict_type=UploadConflictReport.ConflictType.LECTURER,
                affected_unit=mappings.get("unit"),
                affected_room=mappings.get("room"),
                affected_lecturer=mappings.get("lecturer"),
                description=f"Row {row_number}: lecturer already assigned at this time.",
                severity=UploadConflictReport.Severity.HIGH,
            ))
        if duplicate_conflicts.exists():
            conflicts.append(UploadConflictReport(
                upload=upload,
                conflict_type=UploadConflictReport.ConflictType.DUPLICATE,
                affected_unit=mappings.get("unit"),
                affected_room=mappings.get("room"),
                affected_lecturer=mappings.get("lecturer"),
                description=f"Row {row_number}: duplicate timetable session.",
                severity=UploadConflictReport.Severity.CRITICAL,
            ))

        if conflicts:
            UploadConflictReport.objects.bulk_create(conflicts)
        return conflicts