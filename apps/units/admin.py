from django.contrib import admin
from apps.units.models import Unit


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name", "department", "credit_hours", "status")
    list_filter = ("department", "status")
    search_fields = ("code", "name")
from django.contrib import admin

from .models import Unit


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
	list_display = ("code", "title", "department", "credit_hours")
	list_filter = ("department",)
	search_fields = ("code", "title")
