from django.urls import path

from apps.curriculum.views import (
	CurriculumDetailAPIView,
	CurriculumListCreateAPIView,
	StudentUnitsAPIView,
)

urlpatterns = [
	path("", CurriculumListCreateAPIView.as_view(), name="curriculum-list-create"),
	path("student-units/", StudentUnitsAPIView.as_view(), name="curriculum-student-units"),
	path("<uuid:pk>/", CurriculumDetailAPIView.as_view(), name="curriculum-detail"),
]
