from __future__ import annotations

from apps.uploads.selectors import UploadSelector


class UploadReportingService:
    @staticmethod
    def build_report(upload_id: str) -> dict:
        upload = UploadSelector.get_upload(upload_id)
        logs = UploadSelector.logs_for_upload(upload_id)
        conflicts = UploadSelector.conflicts_for_upload(upload_id)
        stats = UploadSelector.stats_for_upload(upload_id)
        return {
            "upload_id": str(upload.id),
            "original_filename": upload.original_filename,
            "processing_status": upload.processing_status,
            "total_rows": upload.total_rows,
            "successful_rows": upload.successful_rows,
            "failed_rows": upload.failed_rows,
            "summary": {
                "logs_total": stats["logs_total"],
                "conflicts_total": stats["conflicts_total"],
                "conflicts_by_type": stats["conflicts_by_type"],
            },
            "logs": [
                {
                    "row_number": log.row_number,
                    "status": log.status,
                    "error_message": log.error_message,
                    "raw_data": log.raw_data,
                }
                for log in logs
            ],
            "conflicts": [
                {
                    "conflict_type": conflict.conflict_type,
                    "description": conflict.description,
                    "severity": conflict.severity,
                }
                for conflict in conflicts
            ],
        }