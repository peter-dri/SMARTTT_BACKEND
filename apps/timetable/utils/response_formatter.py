"""
Response formatting utilities for consistent API responses.

Ensures all API responses follow a standard format with proper
status codes, error tracking, and detailed messages.
"""

from typing import Optional, Dict, Any, List
from enum import Enum


class ResponseStatus(str, Enum):
    """Standard response status values."""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    PARTIAL = "partial"  # Some rows processed, some failed


class TimetableResponseFormatter:
    """
    Formats API responses for timetable operations.
    
    Ensures consistent response structure across all endpoints.
    """
    
    @staticmethod
    def upload_response(
        upload_batch_id: str,
        rows_received: int,
        rows_saved: int,
        rows_failed: int,
        validation_errors: Optional[List[Dict[str, Any]]] = None,
        conflicts_detected: int = 0,
        status: str = ResponseStatus.SUCCESS,
    ) -> Dict[str, Any]:
        """
        Generate response for timetable upload operation.
        
        Args:
            upload_batch_id: ID of the upload batch
            rows_received: Total rows in uploaded file
            rows_saved: Number of rows successfully saved
            rows_failed: Number of rows that failed
            validation_errors: List of validation error details
            conflicts_detected: Number of conflicts detected
            status: Response status
            
        Returns:
            Formatted response dictionary
        """
        success_rate = (rows_saved / rows_received * 100) if rows_received > 0 else 0
        
        return {
            "status": status,
            "upload_batch_id": upload_batch_id,
            "summary": {
                "rows_received": rows_received,
                "rows_saved": rows_saved,
                "rows_failed": rows_failed,
                "success_rate": round(success_rate, 2),
                "conflicts_detected": conflicts_detected,
            },
            "errors": validation_errors or [],
            "message": f"Upload processed: {rows_saved} of {rows_received} rows saved.",
        }
    
    @staticmethod
    def conflict_response(
        conflicts: List[Dict[str, Any]],
        total_conflicts: int,
        conflict_by_type: Optional[Dict[str, int]] = None,
    ) -> Dict[str, Any]:
        """
        Generate response for conflict detection results.
        
        Args:
            conflicts: List of detected conflicts
            total_conflicts: Total number of conflicts
            conflict_by_type: Breakdown of conflicts by type
            
        Returns:
            Formatted response dictionary
        """
        return {
            "status": ResponseStatus.SUCCESS,
            "summary": {
                "total_conflicts": total_conflicts,
                "by_type": conflict_by_type or {},
            },
            "conflicts": conflicts,
            "message": f"Found {total_conflicts} conflict(s) in timetable.",
        }
    
    @staticmethod
    def error_response(
        error_code: str,
        error_message: str,
        details: Optional[List[str]] = None,
        status: str = ResponseStatus.ERROR,
    ) -> Dict[str, Any]:
        """
        Generate standardized error response.
        
        Args:
            error_code: Machine-readable error code
            error_message: Human-readable error message
            details: Detailed error information
            status: Response status
            
        Returns:
            Formatted error response dictionary
        """
        return {
            "status": status,
            "error": {
                "code": error_code,
                "message": error_message,
                "details": details or [],
            },
        }
    
    @staticmethod
    def validation_error_response(
        field_errors: Dict[str, List[str]],
        general_errors: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Generate response for validation errors.
        
        Args:
            field_errors: Mapping of field names to error lists
            general_errors: General validation errors not tied to specific fields
            
        Returns:
            Formatted validation error response
        """
        return {
            "status": ResponseStatus.ERROR,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation failed",
                "field_errors": field_errors,
                "general_errors": general_errors or [],
            },
        }
