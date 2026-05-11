from rest_framework.routers import DefaultRouter
from django.urls import path, include
from apps.curriculum.views.views import CurriculumViewSet, StudentUnitsView

router = DefaultRouter()
router.register(r"curriculum", CurriculumViewSet, basename="curriculum")

urlpatterns = [
    path("", include(router.urls)),
    path("student-units/", StudentUnitsView.as_view(), name="student-units"),
]
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
