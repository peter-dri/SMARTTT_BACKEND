from __future__ import annotations

from django.db import models

from apps.uploads.models import TimetableUpload, UploadConflictReport, UploadProcessingLog


class UploadSelector:
    @staticmethod
    def base_queryset() -> models.QuerySet:
        return TimetableUpload.objects.select_related("uploaded_by", "department", "program")

    @staticmethod
    def list_uploads(*, department_id: str | None = None, status: str | None = None, uploaded_by_id: str | None = None) -> models.QuerySet:
        queryset = UploadSelector.base_queryset()
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        if status:
            queryset = queryset.filter(processing_status=status)
        if uploaded_by_id:
            queryset = queryset.filter(uploaded_by_id=uploaded_by_id)
        return queryset.order_by("-uploaded_at")

    @staticmethod
    def get_upload(upload_id: str) -> TimetableUpload:
        return UploadSelector.base_queryset().get(id=upload_id)

    @staticmethod
    def logs_for_upload(upload_id: str) -> models.QuerySet:
        return UploadProcessingLog.objects.filter(upload_id=upload_id).order_by("row_number", "created_at")

    @staticmethod
    def conflicts_for_upload(upload_id: str) -> models.QuerySet:
        return UploadConflictReport.objects.select_related("affected_unit", "affected_room", "affected_lecturer").filter(upload_id=upload_id).order_by("-created_at")

    @staticmethod
    def stats_for_upload(upload_id: str) -> dict:
        logs = UploadSelector.logs_for_upload(upload_id)
        conflicts = UploadSelector.conflicts_for_upload(upload_id)
        return {
            "logs_total": logs.count(),
            "successful_rows": logs.filter(status="success").count(),
            "failed_rows": logs.filter(status="failed").count(),
            "conflicts_total": conflicts.count(),
            "conflicts_by_type": {
                row["conflict_type"]: row["count"]
                for row in conflicts.values("conflict_type").annotate(count=models.Count("id"))
            },
        }