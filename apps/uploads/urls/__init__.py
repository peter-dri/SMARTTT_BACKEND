from django.urls import path

from apps.uploads.views import (
    TimetableUploadConflictListAPIView,
    TimetableUploadCreateAPIView,
    TimetableUploadDetailAPIView,
    TimetableUploadListAPIView,
    TimetableUploadLogListAPIView,
    TimetableUploadReprocessAPIView,
    TimetableUploadReportAPIView,
    TimetableUploadValidateAPIView,
)

urlpatterns = [
    path("", TimetableUploadListAPIView.as_view(), name="upload-list"),
    path("timetable/", TimetableUploadCreateAPIView.as_view(), name="upload-create"),
    path("validate/", TimetableUploadValidateAPIView.as_view(), name="upload-validate"),
    path("reprocess/<uuid:pk>/", TimetableUploadReprocessAPIView.as_view(), name="upload-reprocess"),
    path("<uuid:pk>/", TimetableUploadDetailAPIView.as_view(), name="upload-detail"),
    path("<uuid:pk>/logs/", TimetableUploadLogListAPIView.as_view(), name="upload-logs"),
    path("<uuid:pk>/conflicts/", TimetableUploadConflictListAPIView.as_view(), name="upload-conflicts"),
    path("<uuid:pk>/report/", TimetableUploadReportAPIView.as_view(), name="upload-report"),
]