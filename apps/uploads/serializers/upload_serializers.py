from __future__ import annotations

from rest_framework import serializers

from apps.uploads.models import TimetableUpload, UploadConflictReport, UploadProcessingLog
from apps.uploads.validators import ExcelFileValidator


class UploadProcessingLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadProcessingLog
        fields = ("id", "row_number", "status", "error_message", "raw_data", "created_at")
        read_only_fields = fields


class UploadConflictReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadConflictReport
        fields = (
            "id",
            "conflict_type",
            "affected_unit",
            "affected_room",
            "affected_lecturer",
            "description",
            "severity",
            "created_at",
        )
        read_only_fields = fields


class TimetableUploadListSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source="uploaded_by.get_full_name", read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)
    program_name = serializers.CharField(source="program.name", read_only=True)

    class Meta:
        model = TimetableUpload
        fields = (
            "id",
            "uploaded_by",
            "uploaded_by_name",
            "department",
            "department_name",
            "program",
            "program_name",
            "upload_type",
            "original_filename",
            "processing_status",
            "total_rows",
            "successful_rows",
            "failed_rows",
            "uploaded_at",
            "processed_at",
        )
        read_only_fields = fields


class TimetableUploadDetailSerializer(TimetableUploadListSerializer):
    logs = UploadProcessingLogSerializer(many=True, read_only=True, source="processing_logs")
    conflicts = UploadConflictReportSerializer(many=True, read_only=True, source="conflict_reports")

    class Meta(TimetableUploadListSerializer.Meta):
        fields = TimetableUploadListSerializer.Meta.fields + ("error_summary", "logs", "conflicts")


class TimetableUploadCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimetableUpload
        fields = ("id", "uploaded_file", "department", "program", "upload_type")
        read_only_fields = ("id",)

    def validate_uploaded_file(self, uploaded_file):
        ExcelFileValidator.validate(uploaded_file)
        return uploaded_file

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["uploaded_by"] = request.user
        validated_data["original_filename"] = validated_data["uploaded_file"].name
        return super().create(validated_data)


class TimetableUploadValidateSerializer(serializers.Serializer):
    uploaded_file = serializers.FileField()

    def validate_uploaded_file(self, uploaded_file):
        ExcelFileValidator.validate(uploaded_file)
        return uploaded_file


class TimetableUploadReportSerializer(serializers.Serializer):
    upload_id = serializers.UUIDField()
    original_filename = serializers.CharField()
    processing_status = serializers.CharField()
    total_rows = serializers.IntegerField()
    successful_rows = serializers.IntegerField()
    failed_rows = serializers.IntegerField()
    summary = serializers.DictField()
    logs = serializers.ListField()
    conflicts = serializers.ListField()