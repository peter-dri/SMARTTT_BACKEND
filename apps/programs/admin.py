from django.contrib import admin
from apps.programs.models import Program


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "code", "department", "duration_years", "status")
    list_filter = ("department", "status")
    search_fields = ("name", "code")
from django.contrib import admin

from .models import Program


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
	list_display = ("code", "name", "department", "duration_years")
	list_filter = ("department",)
	search_fields = ("code", "name")
