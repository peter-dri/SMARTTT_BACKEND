"""
URL Configuration for timetable app.

API Endpoints:
- /api/v1/timetable/rooms/ - Room management
- /api/v1/timetable/timeslots/ - TimeSlot management
- /api/v1/timetable/sessions/ - Timetable session management
- /api/v1/timetable/sessions/my-timetable/ - Student personalized timetable
- /api/v1/timetable/sessions/lecturer-schedule/ - Lecturer teaching schedule
- /api/v1/timetable/sessions/conflicts/ - Conflict reporting
- /api/v1/timetable/terms/ - Academic terms management
- /api/v1/timetable/slots/ - Timetable slots/sessions (legacy)
- /api/v1/timetable/uploads/ - Upload history
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.timetable.views import (
    RoomViewSet,
    TimeSlotViewSet,
    TimetableSessionViewSet,
    AcademicTermViewSet,
    TimetableConflictViewSet,
    TimetableSlotViewSet,
    TimetableUploadListViewSet,
    TimetableUploadAPIView,
)

router = DefaultRouter()

# New production endpoints
router.register("rooms", RoomViewSet, basename="room")
router.register("timeslots", TimeSlotViewSet, basename="timeslot")
router.register("sessions", TimetableSessionViewSet, basename="timetable-session")

# Legacy endpoints (for backward compatibility)
router.register("terms", AcademicTermViewSet, basename="academic-terms")
router.register("slots", TimetableSlotViewSet, basename="timetable-slots")
router.register("conflicts", TimetableConflictViewSet, basename="timetable-conflicts")
router.register("uploads", TimetableUploadListViewSet, basename="timetable-uploads")

urlpatterns = [
    path("", include(router.urls)),
    path("upload/", TimetableUploadAPIView.as_view(), name="timetable-upload"),
]

