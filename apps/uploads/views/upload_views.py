from __future__ import annotations

from rest_framework import generics, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.utils import is_registrar, is_super_admin
from apps.curriculum.utils import get_user_department_id
from apps.uploads.permissions import CanManageTimetableUploads, CanViewTimetableUploads
from apps.uploads.selectors import UploadSelector
from apps.uploads.serializers import (
    TimetableUploadCreateSerializer,
    TimetableUploadDetailSerializer,
    TimetableUploadListSerializer,
    TimetableUploadReportSerializer,
    TimetableUploadValidateSerializer,
    UploadConflictReportSerializer,
    UploadProcessingLogSerializer,
)
from apps.uploads.services import UploadProcessingService, UploadReportingService


class TimetableUploadListAPIView(generics.ListAPIView):
    serializer_class = TimetableUploadListSerializer
    permission_classes = [CanViewTimetableUploads]

    def get_queryset(self):
        queryset = UploadSelector.list_uploads(
            department_id=self.request.query_params.get("department"),
            status=self.request.query_params.get("processing_status"),
            uploaded_by_id=self.request.query_params.get("uploaded_by"),
        )
        if is_super_admin(self.request.user) or is_registrar(self.request.user):
            return queryset
        user_department_id = get_user_department_id(self.request.user)
        if user_department_id:
            return queryset.filter(department_id=user_department_id)
        return queryset.none()


class TimetableUploadCreateAPIView(generics.CreateAPIView):
    serializer_class = TimetableUploadCreateSerializer
    permission_classes = [CanManageTimetableUploads]
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        upload = serializer.save()
        processed_upload = UploadProcessingService.process_upload(upload=upload)
        return Response(TimetableUploadDetailSerializer(processed_upload).data, status=status.HTTP_201_CREATED)


class TimetableUploadDetailAPIView(generics.RetrieveAPIView):
    serializer_class = TimetableUploadDetailSerializer
    permission_classes = [CanViewTimetableUploads]
    queryset = UploadSelector.base_queryset()
class TimetableUploadLogListAPIView(generics.ListAPIView):
    serializer_class = UploadProcessingLogSerializer
    permission_classes = [CanViewTimetableUploads]

    def get_queryset(self):
        upload = UploadSelector.get_upload(self.kwargs["pk"])
        self.check_object_permissions(self.request, upload)
        return UploadSelector.logs_for_upload(upload.id)


class TimetableUploadConflictListAPIView(generics.ListAPIView):
    serializer_class = UploadConflictReportSerializer
    permission_classes = [CanViewTimetableUploads]

    def get_queryset(self):
        upload = UploadSelector.get_upload(self.kwargs["pk"])
        self.check_object_permissions(self.request, upload)
        return UploadSelector.conflicts_for_upload(upload.id)


class TimetableUploadReportAPIView(APIView):
    permission_classes = [CanViewTimetableUploads]

    def get(self, request, pk):
        upload = UploadSelector.get_upload(pk)
        self.check_object_permissions(request, upload)
        report = UploadReportingService.build_report(pk)
        serializer = TimetableUploadReportSerializer(data=report)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)


class TimetableUploadValidateAPIView(APIView):
    permission_classes = [CanManageTimetableUploads]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = TimetableUploadValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"status": "valid", "message": "File structure validation passed."})


class TimetableUploadReprocessAPIView(APIView):
    permission_classes = [CanManageTimetableUploads]

    def post(self, request, pk):
        upload = UploadSelector.get_upload(pk)
        self.check_object_permissions(request, upload)
        processed_upload = UploadProcessingService.reprocess_upload(upload=upload)
        return Response(TimetableUploadDetailSerializer(processed_upload).data)