from __future__ import annotations

from django.utils import timezone

from apps.timetable.models import TimetableSession
from apps.uploads.models import TimetableUpload, UploadProcessingLog
from apps.uploads.services import (
    ExcelParserService,
    TimetableMappingService,
    TimetableSessionCreationService,
    UploadConflictService,
)
from apps.uploads.validators import ExcelFileValidator, ExcelStructureValidator, TimetableDataValidator


class UploadProcessingService:
    @staticmethod
    def _store_log(*, upload: TimetableUpload, row_number: int, status: str, error_message: str = "", raw_data: dict | None = None) -> None:
        UploadProcessingLog.objects.create(
            upload=upload,
            row_number=row_number,
            status=status,
            error_message=error_message,
            raw_data=raw_data or {},
        )

    @staticmethod
    def process_upload(*, upload: TimetableUpload) -> TimetableUpload:
        ExcelFileValidator.validate(upload.uploaded_file)
        upload.processing_status = TimetableUpload.ProcessingStatus.VALIDATING
        upload.save(update_fields=["processing_status", "updated_at"])

        dataframe = ExcelParserService.read_workbook(upload.uploaded_file)
        ExcelStructureValidator.validate_columns(dataframe.columns)
        parsed_rows = ExcelParserService.parse_rows(dataframe)

        upload.total_rows = len(parsed_rows)
        upload.processing_status = TimetableUpload.ProcessingStatus.PROCESSING
        upload.save(update_fields=["total_rows", "processing_status", "updated_at"])

        session_payloads: list[dict] = []
        successful_rows = 0
        failed_rows = 0
        validation_errors: list[dict] = []

        for parsed_row in parsed_rows:
            mappings = TimetableMappingService.build_mapping(parsed_row.normalized_data)
            row_errors = TimetableDataValidator.validate_row(
                parsed_row.normalized_data,
                row_number=parsed_row.row_number,
                mappings=mappings,
            )
            if row_errors:
                failed_rows += 1
                error_message = "; ".join(row_errors)
                validation_errors.append({"row_number": parsed_row.row_number, "errors": row_errors})
                UploadProcessingService._store_log(
                    upload=upload,
                    row_number=parsed_row.row_number,
                    status=UploadProcessingLog.Status.FAILED,
                    error_message=error_message,
                    raw_data=parsed_row.raw_data,
                )
                continue

            conflict_records = UploadConflictService.detect_for_row(
                upload=upload,
                row_number=parsed_row.row_number,
                row=parsed_row.normalized_data,
                mappings=mappings,
            )
            if conflict_records:
                failed_rows += 1
                error_message = "; ".join(record.description for record in conflict_records)
                validation_errors.append({"row_number": parsed_row.row_number, "errors": [record.description for record in conflict_records]})
                UploadProcessingService._store_log(
                    upload=upload,
                    row_number=parsed_row.row_number,
                    status=UploadProcessingLog.Status.SKIPPED,
                    error_message=error_message,
                    raw_data=parsed_row.raw_data,
                )
                continue

            session_payloads.append(
                {
                    "unit": mappings["unit"],
                    "program": mappings["program"],
                    "department": mappings["department"],
                    "lecturer": mappings["lecturer"],
                    "room": mappings["room"],
                    "time_slot": mappings["time_slot"],
                    "academic_year": parsed_row.normalized_data["academic_year"],
                    "study_year": parsed_row.normalized_data["study_year"],
                    "semester": parsed_row.normalized_data["semester"],
                    "day_of_week": parsed_row.normalized_data["day"],
                    "session_type": parsed_row.normalized_data.get("session_type") or TimetableSession.SessionType.LECTURE,
                    "delivery_mode": parsed_row.normalized_data.get("delivery_mode") or TimetableSession.DeliveryMode.FACE_TO_FACE,
                    "student_group": mappings["student_group"],
                    "max_students": getattr(mappings["room"], "capacity", 0) if mappings.get("room") else 0,
                    "created_by": upload.uploaded_by,
                    "notes": parsed_row.normalized_data.get("notes", "") or "",
                    "status": TimetableSession.Status.SCHEDULED,
                }
            )
            successful_rows += 1
            UploadProcessingService._store_log(
                upload=upload,
                row_number=parsed_row.row_number,
                status=UploadProcessingLog.Status.SUCCESS,
                raw_data=parsed_row.raw_data,
            )

        created_sessions = []
        if session_payloads:
            created_sessions = TimetableSessionCreationService.bulk_create_sessions(session_payloads)

        upload.successful_rows = len(created_sessions)
        upload.failed_rows = failed_rows
        upload.error_summary = {"row_errors": validation_errors}
        upload.processing_status = TimetableUpload.ProcessingStatus.PROCESSED if failed_rows == 0 else TimetableUpload.ProcessingStatus.PARTIAL
        upload.processed_at = timezone.now()
        upload.save(update_fields=["successful_rows", "failed_rows", "error_summary", "processing_status", "processed_at", "updated_at"])
        return upload

    @staticmethod
    def reprocess_upload(*, upload: TimetableUpload) -> TimetableUpload:
        return UploadProcessingService.process_upload(upload=upload)