from typing import List, Dict, Any, Tuple
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from apps.curriculum.models import CurriculumUnit
from apps.lecturers.models import Lecturer
from apps.rooms.models import Room
from apps.timetable.models import AcademicTerm, TimetableSlot
from apps.timetable.utils import (
    DatabaseOperationException,
    ResourceNotFoundException,
    DuplicateSessionException,
    TimetableLogger,
)


class TimetablePersistenceService:
    def __init__(self):
        """Initialize service with logging."""
        self.logger = TimetableLogger()
    
    @transaction.atomic
    def save_rows(
        self,
        upload_batch,
        rows: List[Dict[str, Any]]
    ) -> Tuple[List[TimetableSlot], List[Dict[str, Any]]]:
        saved_slots = []
        errors = []
        
        for idx, row in enumerate(rows, 1):
            try:
                # Check for existence before creating
                slot = self._get_or_create_slot(upload_batch, row)
                saved_slots.append(slot)
                
            except DuplicateSessionException as e:
                errors.append({
                    "row_number": idx,
                    "error": str(e),
                    "error_code": "DUPLICATE_SESSION",
                    "data": {k: v for k, v in row.items() if k not in ["start_time", "end_time"]}
                })
            except ResourceNotFoundException as e:
                errors.append({
                    "row_number": idx,
                    "error": str(e),
                    "error_code": "RESOURCE_NOT_FOUND",
                    "data": {k: v for k, v in row.items() if k not in ["start_time", "end_time"]}
                })
            except Exception as e:
                errors.append({
                    "row_number": idx,
                    "error": f"Unexpected error: {str(e)}",
                    "error_code": "DATABASE_ERROR",
                    "data": {k: v for k, v in row.items() if k not in ["start_time", "end_time"]}
                })
                self.logger.log_database_error(
                    "CREATE_SLOT",
                    str(e),
                    upload_batch.id
                )
        
        if not saved_slots and errors:
            raise DatabaseOperationException(
                f"Failed to save any timetable slots. Errors: {len(errors)}"
            )
        
        return saved_slots, errors
    
    def _get_or_create_slot(
        self,
        upload_batch,
        row: Dict[str, Any]
    ) -> TimetableSlot:
        # Get AcademicTerm
        try:
            term = AcademicTerm.objects.get(
                academic_year=row["academic_year"],
                semester=row["semester"]
            )
        except AcademicTerm.DoesNotExist:
            raise ResourceNotFoundException(
                f"Academic term not found: {row['academic_year']} S{row['semester']}"
            )
        
        # Get CurriculumUnit
        try:
            curriculum_unit = CurriculumUnit.objects.select_related(
                "curriculum",
                "unit"
            ).get(
                curriculum__program__code=row["program_code"],
                unit__code=row["unit_code"],
                curriculum__study_year=row["year_of_study"],
                curriculum__semester=row["semester"]
            )
        except CurriculumUnit.DoesNotExist:
            raise ResourceNotFoundException(
                f"Curriculum unit not found: {row['program_code']}/{row['unit_code']} "
                f"Year {row['year_of_study']} Sem {row['semester']}"
            )
        
        # Get Room
        try:
            room = Room.objects.get(code=row["room_code"])
        except Room.DoesNotExist:
            raise ResourceNotFoundException(
                f"Room not found: {row['room_code']}"
            )
        
        # Get Lecturer
        try:
            lecturer = Lecturer.objects.select_related("user").get(
                user__university_id=row["lecturer_university_id"]
            )
        except Lecturer.DoesNotExist:
            raise ResourceNotFoundException(
                f"Lecturer not found: {row['lecturer_university_id']}"
            )
        
        # Check for duplicate
        existing = TimetableSlot.objects.filter(
            term=term,
            curriculum_unit=curriculum_unit,
            lecturer=lecturer,
            room=room,
            day_of_week=row["day_of_week"],
            start_time=row["start_time"],
            end_time=row["end_time"],
            class_group=row["class_group"],
        ).exists()
        
        if existing:
            raise DuplicateSessionException(
                f"Duplicate session: {curriculum_unit.unit.code} "
                f"{row['day_of_week']} {row['start_time']}-{row['end_time']}"
            )
        
        # Create new slot
        slot = TimetableSlot.objects.create(
            term=term,
            curriculum_unit=curriculum_unit,
            lecturer=lecturer,
            room=room,
            day_of_week=row["day_of_week"],
            start_time=row["start_time"],
            end_time=row["end_time"],
            class_group=row["class_group"],
            upload_batch=upload_batch,
        )
        
        return slot

