from django.urls import path

from apps.personalization.views import PersonalizedTimetableAPIView, PersonalizedUnitsAPIView

app_name = "personalization"

urlpatterns = [
	path("my-timetable/", PersonalizedTimetableAPIView.as_view(), name="my-timetable"),
	path("my-units/", PersonalizedUnitsAPIView.as_view(), name="my-units"),
]
