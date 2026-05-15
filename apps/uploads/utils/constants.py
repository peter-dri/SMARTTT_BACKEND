from django.utils.translation import gettext_lazy as _

SUPPORTED_UPLOAD_EXTENSIONS = {".xlsx", ".xlsm"}
MAX_UPLOAD_FILE_SIZE_BYTES = 25 * 1024 * 1024
DEFAULT_UPLOAD_TYPE = "timetable"

REQUIRED_UPLOAD_COLUMNS = {
    "unit_code",
    "unit_name",
    "program",
    "department",
    "lecturer",
    "room",
    "day",
    "start_time",
    "end_time",
    "semester",
    "study_year",
    "academic_year",
    "session_type",
}

COLUMN_ALIASES = {
    "unit_code": {"unit code", "unit_code", "code", "unitcode"},
    "unit_name": {"unit name", "unit_name", "title", "unittitle"},
    "program": {"program", "programme", "program code", "program_code"},
    "department": {"department", "department code", "department_code"},
    "lecturer": {"lecturer", "lecturer name", "lecturer_name", "lecturer university id", "lecturer_university_id"},
    "room": {"room", "room code", "room_code"},
    "day": {"day", "day of week", "day_of_week"},
    "start_time": {"start time", "start_time", "start"},
    "end_time": {"end time", "end_time", "end"},
    "semester": {"semester", "term"},
    "study_year": {"study year", "study_year", "year of study", "year_of_study"},
    "academic_year": {"academic year", "academic_year", "year"},
    "session_type": {"session type", "session_type", "type"},
    "notes": {"notes", "remarks", "comment"},
    "student_group": {"student group", "student_group", "class group", "class_group"},
    "delivery_mode": {"delivery mode", "delivery_mode"},
    "max_students": {"max students", "max_students", "capacity"},
}

DAY_NORMALIZATION = {
    "mon": "MON",
    "monday": "MON",
    "tue": "TUE",
    "tues": "TUE",
    "tuesday": "TUE",
    "wed": "WED",
    "wednesday": "WED",
    "thu": "THU",
    "thursday": "THU",
    "fri": "FRI",
    "friday": "FRI",
    "sat": "SAT",
    "saturday": "SAT",
    "sun": "SUN",
    "sunday": "SUN",
}

SESSION_TYPE_NORMALIZATION = {
    "lecture": "lecture",
    "lectures": "lecture",
    "practical": "practical",
    "lab": "practical",
    "tutorial": "tutorial",
    "seminar": "seminar",
    "workshop": "workshop",
    "project": "project",
    "field work": "field_work",
    "field_work": "field_work",
}

DELIVERY_MODE_NORMALIZATION = {
    "face to face": "face_to_face",
    "face_to_face": "face_to_face",
    "online": "online",
    "hybrid": "hybrid",
    "blended": "blended",
}

PROCESSING_STATUS_LABELS = {
    "received": _("Received"),
    "validating": _("Validating"),
    "processing": _("Processing"),
    "partial": _("Partial"),
    "processed": _("Processed"),
    "failed": _("Failed"),
}
