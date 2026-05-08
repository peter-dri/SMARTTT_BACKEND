"""
URL Configuration for timetable app.

API Endpoints:
- /api/timetable/terms/ - Academic terms management
- /api/timetable/slots/ - Timetable slots/sessions
- /api/timetable/conflicts/ - Conflict reporting
- /api/timetable/uploads/ - Upload history
- /api/timetable/upload/ - Upload new timetable file
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.timetable.views import (
    AcademicTermViewSet,
    TimetableConflictViewSet,
    TimetableSlotViewSet,
    TimetableUploadListViewSet,
    TimetableUploadAPIView,
)

router = DefaultRouter()
router.register("terms", AcademicTermViewSet, basename="academic-terms")
router.register("slots", TimetableSlotViewSet, basename="timetable-slots")
router.register("conflicts", TimetableConflictViewSet, basename="timetable-conflicts")
router.register("uploads", TimetableUploadListViewSet, basename="timetable-uploads")

urlpatterns = [
    path("", include(router.urls)),
    path("upload/", TimetableUploadAPIView.as_view(), name="timetable-upload"),
]

