from django.contrib import admin
from apps.timetable.models import (
    AcademicTerm,
    TimetableUploadBatch,
    TimetableSlot,
    TimetableConflict,
)


@admin.register(AcademicTerm)
class AcademicTermAdmin(admin.ModelAdmin):
    list_display = ("id", "academic_year", "semester", "start_date", "end_date", "is_current")
    list_filter = ("is_current", "academic_year", "semester")
    search_fields = ("academic_year",)


@admin.register(TimetableUploadBatch)
class TimetableUploadBatchAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "rows_received", "rows_saved", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("uploaded_by__last_name", "uploaded_by__first_name", "id")


@admin.register(TimetableSlot)
class TimetableSlotAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "term",
        "unit",
        "lecturer",
        "room",
        "day_of_week",
        "start_time",
        "end_time",
    )
    list_filter = ("term", "day_of_week", "room")
    search_fields = (
        "unit__code",
        "unit__name",
        "room__code",
        "room__building",
        "lecturer__user__university_id",
        "lecturer__user__first_name",
        "lecturer__user__last_name",
        "class_group",
    )


@admin.register(TimetableConflict)
class TimetableConflictAdmin(admin.ModelAdmin):
    list_display = ("id", "conflict_type", "term", "created_at")
    list_filter = ("conflict_type", "term")
    search_fields = ("conflict_type",)
