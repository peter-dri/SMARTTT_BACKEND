from django.contrib import admin
from apps.departments.models import Faculty, Department, DepartmentAdmin


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "code")
    search_fields = ("name", "code")


@admin.register(Department)
class DepartmentAdminModel(admin.ModelAdmin):
    list_display = ("id", "name", "code", "faculty", "status")
    list_filter = ("faculty", "status")
    search_fields = ("name", "code")


@admin.register(DepartmentAdmin)
class DepartmentAdminAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "department", "role", "assigned_at")
    list_filter = ("role",)
from django.contrib import admin
from apps.departments.models import Faculty, Department, DepartmentAdmin


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")


@admin.register(Department)
class DepartmentAdminModel(admin.ModelAdmin):
    list_display = ("name", "code", "faculty", "status")
    list_filter = ("faculty", "status")
    search_fields = ("name", "code")


@admin.register(DepartmentAdmin)
class DepartmentAdminAssignment(admin.ModelAdmin):
    list_display = ("user", "department", "role", "assigned_at")
    list_filter = ("role",)
from django.contrib import admin

from .models import Department


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
	list_display = ("code", "name")
	search_fields = ("code", "name")
