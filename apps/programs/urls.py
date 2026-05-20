from rest_framework.routers import DefaultRouter
from django.urls import path, include
from apps.programs.views.views import ProgramViewSet

router = DefaultRouter()
router.register(r"programs", ProgramViewSet, basename="program")

urlpatterns = [path("", include(router.urls))]
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.programs.views import ProgramViewSet

router = DefaultRouter()
router.register("programs", ProgramViewSet, basename="programs")

urlpatterns = [path("", include(router.urls))]
