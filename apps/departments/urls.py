from rest_framework.routers import DefaultRouter
from django.urls import path, include
from apps.departments.views.views import FacultyViewSet, DepartmentViewSet, DepartmentAdminViewSet

router = DefaultRouter()
router.register(r"faculties", FacultyViewSet, basename="faculty")
router.register(r"departments", DepartmentViewSet, basename="department")
router.register(r"department-admins", DepartmentAdminViewSet, basename="departmentadmin")

urlpatterns = [
    path("", include(router.urls)),
]
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.departments.views import DepartmentViewSet

router = DefaultRouter()
router.register("departments", DepartmentViewSet, basename="departments")

urlpatterns = [path("", include(router.urls))]
