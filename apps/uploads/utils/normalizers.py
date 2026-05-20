from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time
from typing import Any

import pandas as pd

from .constants import (
    COLUMN_ALIASES,
    DAY_NORMALIZATION,
    DELIVERY_MODE_NORMALIZATION,
    SESSION_TYPE_NORMALIZATION,
)


def normalize_column_name(value: Any) -> str:
    normalized = str(value or "").strip().lower().replace("/", " ").replace("-", " ")
    normalized = " ".join(normalized.split())
    for canonical, aliases in COLUMN_ALIASES.items():
        if normalized == canonical or normalized in aliases:
            return canonical
    return normalized.replace(" ", "_")


def clean_text(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None
    text = str(value).strip()
    return text or None


def normalize_day(value: Any) -> str | None:
    text = clean_text(value)
    if not text:
        return None
    return DAY_NORMALIZATION.get(text.lower(), text[:3].upper())


def normalize_session_type(value: Any) -> str:
    text = clean_text(value)
    if not text:
        return "lecture"
    return SESSION_TYPE_NORMALIZATION.get(text.lower(), text.lower().replace(" ", "_"))


def normalize_delivery_mode(value: Any) -> str:
    text = clean_text(value)
    if not text:
        return "face_to_face"
    return DELIVERY_MODE_NORMALIZATION.get(text.lower(), text.lower().replace(" ", "_"))


def parse_time_value(value: Any) -> time | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, time):
        return value
    if isinstance(value, datetime):
        return value.time()
    if hasattr(value, "time") and callable(value.time):
        try:
            return value.time()
        except Exception:
            pass
    text = clean_text(value)
    if not text:
        return None
    parsed = pd.to_datetime(text, errors="coerce")
    if pd.notna(parsed):
        return parsed.time()
    for format_string in ("%H:%M", "%H:%M:%S", "%I:%M %p", "%I:%M%p"):
        try:
            return datetime.strptime(text, format_string).time()
        except ValueError:
            continue
    return None


def normalize_row_payload(row: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for key, value in row.items():
        canonical_key = normalize_column_name(key)
        if canonical_key in {"start_time", "end_time"}:
            normalized[canonical_key] = parse_time_value(value)
        elif canonical_key == "semester":
            try:
                normalized[canonical_key] = int(value) if clean_text(value) is not None else None
            except (TypeError, ValueError):
                normalized[canonical_key] = None
        elif canonical_key == "study_year":
            try:
                normalized[canonical_key] = int(value) if clean_text(value) is not None else None
            except (TypeError, ValueError):
                normalized[canonical_key] = None
        elif canonical_key == "day":
            normalized[canonical_key] = normalize_day(value)
        elif canonical_key == "session_type":
            normalized[canonical_key] = normalize_session_type(value)
        elif canonical_key == "delivery_mode":
            normalized[canonical_key] = normalize_delivery_mode(value)
        else:
            normalized[canonical_key] = clean_text(value)
    return normalized


def build_student_group(row: dict[str, Any]) -> str:
    explicit_group = clean_text(row.get("student_group"))
    if explicit_group:
        return explicit_group
    program = clean_text(row.get("program")) or "PROGRAM"
    study_year = clean_text(row.get("study_year")) or "Y"
    semester = clean_text(row.get("semester")) or "S"
    return f"{program}-{study_year}-{semester}"


@dataclass(frozen=True)
class ParsedWorkbookRow:
    row_number: int
    raw_data: dict[str, Any]
    normalized_data: dict[str, Any]
