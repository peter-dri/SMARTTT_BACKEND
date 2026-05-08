"""
Logging utilities for timetable operations.

Production-level logging for tracking file uploads, data processing,
and conflict detection.
"""

import json
import logging
from typing import Any, Dict, Optional
from datetime import datetime


logger = logging.getLogger("timetable")


class TimetableLogger:
    """
    Centralized logging for timetable operations.
    
    Ensures consistent structure and format for all logs.
    """
    
    @staticmethod
    def _format_log_entry(
        operation: str,
        status: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Format log entry with timestamp and details."""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "operation": operation,
            "status": status,
            "details": details or {},
        }
    
    @staticmethod
    def log_upload_started(upload_batch_id: str, file_name: str) -> None:
        """Log when upload processing starts."""
        entry = TimetableLogger._format_log_entry(
            operation="UPLOAD_STARTED",
            status="INITIATED",
            details={
                "upload_batch_id": str(upload_batch_id),
                "file_name": file_name,
            }
        )
        logger.info(f"Upload started: {json.dumps(entry)}")
    
    @staticmethod
    def log_parsing_started(upload_batch_id: str, rows_count: int) -> None:
        """Log when parsing starts."""
        entry = TimetableLogger._format_log_entry(
            operation="PARSING_STARTED",
            status="IN_PROGRESS",
            details={
                "upload_batch_id": str(upload_batch_id),
                "total_rows": rows_count,
            }
        )
        logger.info(f"Parsing started: {json.dumps(entry)}")
    
    @staticmethod
    def log_validation_error(
        upload_batch_id: str,
        row_number: int,
        field: str,
        error: str,
    ) -> None:
        """Log validation errors during upload processing."""
        entry = TimetableLogger._format_log_entry(
            operation="VALIDATION_ERROR",
            status="ERROR",
            details={
                "upload_batch_id": str(upload_batch_id),
                "row_number": row_number,
                "field": field,
                "error": error,
            }
        )
        logger.warning(f"Validation error: {json.dumps(entry)}")
    
    @staticmethod
    def log_upload_completed(
        upload_batch_id: str,
        rows_received: int,
        rows_saved: int,
        conflicts_detected: int,
    ) -> None:
        """Log when upload processing completes successfully."""
        entry = TimetableLogger._format_log_entry(
            operation="UPLOAD_COMPLETED",
            status="SUCCESS",
            details={
                "upload_batch_id": str(upload_batch_id),
                "rows_received": rows_received,
                "rows_saved": rows_saved,
                "conflicts_detected": conflicts_detected,
                "success_rate": round((rows_saved / rows_received * 100), 2) if rows_received > 0 else 0,
            }
        )
        logger.info(f"Upload completed: {json.dumps(entry)}")
    
    @staticmethod
    def log_upload_failed(
        upload_batch_id: str,
        error_message: str,
        rows_processed: int = 0,
    ) -> None:
        """Log when upload processing fails."""
        entry = TimetableLogger._format_log_entry(
            operation="UPLOAD_FAILED",
            status="FAILURE",
            details={
                "upload_batch_id": str(upload_batch_id),
                "error_message": error_message,
                "rows_processed": rows_processed,
            }
        )
        logger.error(f"Upload failed: {json.dumps(entry)}")
    
    @staticmethod
    def log_conflict_detected(
        upload_batch_id: str,
        conflict_type: str,
        slot_a_id: str,
        slot_b_id: str,
    ) -> None:
        """Log when conflict is detected."""
        entry = TimetableLogger._format_log_entry(
            operation="CONFLICT_DETECTED",
            status="WARNING",
            details={
                "upload_batch_id": str(upload_batch_id),
                "conflict_type": conflict_type,
                "slot_a_id": str(slot_a_id),
                "slot_b_id": str(slot_b_id),
            }
        )
        logger.warning(f"Conflict detected: {json.dumps(entry)}")
    
    @staticmethod
    def log_database_error(
        operation: str,
        error_message: str,
        upload_batch_id: Optional[str] = None,
    ) -> None:
        """Log database operation errors."""
        entry = TimetableLogger._format_log_entry(
            operation=f"DATABASE_{operation}",
            status="ERROR",
            details={
                "upload_batch_id": str(upload_batch_id) if upload_batch_id else None,
                "error_message": error_message,
            }
        )
        logger.error(f"Database error: {json.dumps(entry)}")
