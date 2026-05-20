from __future__ import annotations

import os

from django.core.files.uploadedfile import UploadedFile
from rest_framework.exceptions import ValidationError

from apps.uploads.utils import MAX_UPLOAD_FILE_SIZE_BYTES, SUPPORTED_UPLOAD_EXTENSIONS


class ExcelFileValidator:
    @staticmethod
    def validate(uploaded_file: UploadedFile) -> None:
        if not uploaded_file:
            raise ValidationError({"file": "An Excel file is required."})
        ExcelFileValidator.validate_extension(uploaded_file.name)
        ExcelFileValidator.validate_size(uploaded_file.size)

    @staticmethod
    def validate_extension(filename: str) -> None:
        extension = os.path.splitext(filename.lower())[1]
        if extension not in SUPPORTED_UPLOAD_EXTENSIONS:
            raise ValidationError({"file": f"Only {', '.join(sorted(SUPPORTED_UPLOAD_EXTENSIONS))} files are supported."})

    @staticmethod
    def validate_size(size: int) -> None:
        if size > MAX_UPLOAD_FILE_SIZE_BYTES:
            raise ValidationError({"file": f"File size exceeds {MAX_UPLOAD_FILE_SIZE_BYTES // (1024 * 1024)}MB."})