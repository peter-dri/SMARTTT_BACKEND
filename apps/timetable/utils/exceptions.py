"""
Exception classes and error handling for timetable operations.

Production-level error definitions with unique error codes for tracking
and debugging purposes.
"""

from rest_framework.exceptions import APIException, ValidationError


class TimetableException(APIException):
    """Base exception for timetable operations."""
    
    status_code = 400
    default_detail = "An error occurred while processing the timetable."
    error_code = "TIMETABLE_ERROR"


class TimetableUploadException(TimetableException):
    """Exception for timetable upload operations."""
    
    error_code = "TIMETABLE_UPLOAD_ERROR"


class FileValidationException(TimetableUploadException):
    """Exception for file validation errors."""
    
    status_code = 400
    error_code = "FILE_VALIDATION_ERROR"


class ExcelParsingException(TimetableUploadException):
    """Exception for Excel parsing errors."""
    
    status_code = 400
    error_code = "EXCEL_PARSING_ERROR"


class DataValidationException(TimetableUploadException):
    """Exception for data validation errors."""
    
    status_code = 422
    error_code = "DATA_VALIDATION_ERROR"


class ConflictDetectionException(TimetableException):
    """Exception for conflict detection errors."""
    
    status_code = 400
    error_code = "CONFLICT_DETECTION_ERROR"


class DatabaseOperationException(TimetableException):
    """Exception for database operation errors."""
    
    status_code = 500
    error_code = "DATABASE_OPERATION_ERROR"


class ResourceNotFoundException(TimetableException):
    """Exception when a required resource is not found."""
    
    status_code = 404
    error_code = "RESOURCE_NOT_FOUND"
    default_detail = "The requested resource was not found."


class DuplicateSessionException(TimetableException):
    """Exception when duplicate timetable sessions are detected."""
    
    status_code = 409
    error_code = "DUPLICATE_SESSION"
    default_detail = "Duplicate timetable session detected."


class UploadStatePreconditionFailedException(TimetableException):
    """Exception when upload is in an invalid state for the requested operation."""
    
    status_code = 409
    error_code = "INVALID_UPLOAD_STATE"
    default_detail = "The upload batch is in an invalid state for this operation."
