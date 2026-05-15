from __future__ import annotations

from collections import Counter

from rest_framework.exceptions import ValidationError

from apps.uploads.utils import REQUIRED_UPLOAD_COLUMNS, normalize_column_name


class ExcelStructureValidator:
    @staticmethod
    def validate_columns(columns) -> dict[str, str]:
        normalized_columns = [normalize_column_name(column) for column in columns]
        duplicate_headers = [header for header, count in Counter(normalized_columns).items() if count > 1]
        missing = sorted(REQUIRED_UPLOAD_COLUMNS - set(normalized_columns))
        if duplicate_headers:
            raise ValidationError({"columns": f"Duplicate headers found: {', '.join(duplicate_headers)}"})
        if missing:
            raise ValidationError({"columns": f"Missing required columns: {', '.join(missing)}"})
        return {original: normalized for original, normalized in zip(columns, normalized_columns)}