"""
Admin configuration for timetable app.

Provides Django admin interface for managing timetable data:
- Academic terms
- Upload batches (with processing status)
- Timetable slots
- Detected conflicts
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count

from .models import AcademicTerm, TimetableConflict, TimetableSlot, TimetableUploadBatch


@admin.register(AcademicTerm)
class AcademicTermAdmin(admin.ModelAdmin):
    """Admin for AcademicTerm model."""
    
    list_display = (
        "academic_year",
        "semester",
        "start_date",
        "end_date",
        "is_current",
        "is_current_badge"
    )
    list_filter = ("academic_year", "semester", "is_current", "created_at")
    search_fields = ("academic_year",)
    ordering = ("-academic_year", "-semester")
    date_hierarchy = "start_date"
    
    fieldsets = (
        ("Term Information", {
            "fields": ("academic_year", "semester", "is_current")
        }),
        ("Duration", {
            "fields": ("start_date", "end_date")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    readonly_fields = ("created_at", "updated_at")
    
    def is_current_badge(self, obj):
        """Display current term status as badge."""
        if obj.is_current:
            return format_html(
                '<span style="background-color: #28a745; color: white; '
                'padding: 3px 8px; border-radius: 3px;">Current</span>'
            )
        return format_html(
            '<span style="background-color: #6c757d; color: white; '
            'padding: 3px 8px; border-radius: 3px;">Inactive</span>'
        )
    is_current_badge.short_description = "Status"


@admin.register(TimetableUploadBatch)
class TimetableUploadBatchAdmin(admin.ModelAdmin):
    """Admin for TimetableUploadBatch model."""
    
    list_display = (
        "id",
        "uploaded_by",
        "status_badge",
        "rows_received",
        "rows_saved",
        "success_rate",
        "error_count",
        "created_at"
    )
    list_filter = ("status", "created_at", "uploaded_by")
    search_fields = ("id", "uploaded_by__email", "source_file")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    readonly_fields = (
        "id",
        "status",
        "rows_received",
        "rows_saved",
        "validation_errors",
        "created_at",
        "updated_at",
        "slot_count",
        "error_details"
    )
    
    fieldsets = (
        ("Upload Information", {
            "fields": ("id", "uploaded_by", "source_file")
        }),
        ("Processing Status", {
            "fields": ("status", "created_at", "updated_at")
        }),
        ("Results Summary", {
            "fields": (
                "rows_received",
                "rows_saved",
                "slot_count",
                "error_count"
            )
        }),
        ("Errors & Details", {
            "fields": ("validation_errors", "error_details"),
            "classes": ("collapse",)
        }),
    )
    
    def status_badge(self, obj):
        """Display processing status as color-coded badge."""
        colors = {
            "received": "#0d6efd",
            "validated": "#0dcaf0",
            "processed": "#198754",
            "failed": "#dc3545"
        }
        color = colors.get(obj.status, "#6c757d")
        return format_html(
            f'<span style="background-color: {color}; color: white; '
            f'padding: 5px 10px; border-radius: 3px; font-weight: bold;">'
            f'{obj.get_status_display()}</span>'
        )
    status_badge.short_description = "Status"
    
    def success_rate(self, obj):
        """Calculate and display success rate."""
        if obj.rows_received == 0:
            return "N/A"
        rate = round((obj.rows_saved / obj.rows_received) * 100, 1)
        
        # Color code: green for 100%, orange for > 50%, red for < 50%
        if rate == 100:
            color = "#198754"
        elif rate >= 50:
            color = "#ffc107"
        else:
            color = "#dc3545"
        
        return format_html(
            f'<span style="color: {color}; font-weight: bold;">{rate}%</span>'
        )
    success_rate.short_description = "Success Rate"
    
    def error_count(self, obj):
        """Count validation errors."""
        count = len(obj.validation_errors) if obj.validation_errors else 0
        if count == 0:
            return "—"
        return format_html(
            f'<span style="background-color: #dc3545; color: white; '
            f'padding: 2px 6px; border-radius: 3px;">{count}</span>'
        )
    error_count.short_description = "Error Count"
    
    def slot_count(self, obj):
        """Display count of slots created from this batch."""
        count = obj.slots.count()
        return format_html(
            f'<strong>{count}</strong> slots created'
        )
    slot_count.short_description = "Slots Created"
    
    def error_details(self, obj):
        """Display error details as formatted list."""
        if not obj.validation_errors:
            return "No errors"
        
        errors_html = "<ul style='margin-left: 20px;'>"
        for error in obj.validation_errors[:10]:  # Show first 10
            errors_html += f"<li>{error}</li>"
        
        if len(obj.validation_errors) > 10:
            errors_html += f"<li><em>... and {len(obj.validation_errors) - 10} more</em></li>"
        
        errors_html += "</ul>"
        return format_html(errors_html)
    error_details.short_description = "Error Details"


@admin.register(TimetableSlot)
class TimetableSlotAdmin(admin.ModelAdmin):
    """Admin for TimetableSlot model."""
    
    list_display = (
        "get_unit_code",
        "get_lecturer_name",
        "room",
        "term",
        "day_of_week",
        "time_slot",
        "class_group",
        "conflict_status"
    )
    list_filter = (
        "term",
        "day_of_week",
        "room",
        "lecturer",
        "upload_batch",
        "created_at"
    )
    search_fields = (
        "curriculum_unit__unit__code",
        "lecturer__user__first_name",
        "lecturer__user__last_name",
        "room__code"
    )
    ordering = ("term", "day_of_week", "start_time")
    readonly_fields = ("id", "created_at", "updated_at", "conflict_count")
    date_hierarchy = "created_at"
    
    fieldsets = (
        ("Session Details", {
            "fields": (
                "term",
                "curriculum_unit",
                "year_of_study",
                "class_group"
            )
        }),
        ("Schedule", {
            "fields": (
                "day_of_week",
                "start_time",
                "end_time"
            )
        }),
        ("Resources", {
            "fields": (
                "lecturer",
                "room"
            )
        }),
        ("Upload Tracking", {
            "fields": ("upload_batch",),
            "classes": ("collapse",)
        }),
        ("Conflicts", {
            "fields": ("conflict_count",),
            "classes": ("collapse",)
        }),
        ("Timestamps", {
            "fields": ("id", "created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    def get_unit_code(self, obj):
        """Display unit code from related curriculum unit."""
        return obj.curriculum_unit.unit.code
    get_unit_code.short_description = "Unit"
    get_unit_code.admin_order_field = "curriculum_unit__unit__code"
    
    def get_lecturer_name(self, obj):
        """Display lecturer's full name."""
        return obj.lecturer.user.get_full_name()
    get_lecturer_name.short_description = "Lecturer"
    get_lecturer_name.admin_order_field = "lecturer__user__first_name"
    
    def time_slot(self, obj):
        """Display formatted time slot."""
        return f"{obj.start_time} - {obj.end_time}"
    time_slot.short_description = "Time"
    
    def conflict_count(self, obj):
        """Display count of conflicts involving this slot."""
        from django.db.models import Q
        count = TimetableConflict.objects.filter(
            Q(slot_a=obj) | Q(slot_b=obj)
        ).count()
        
        if count == 0:
            return format_html(
                '<span style="color: #198754;">No conflicts</span>'
            )
        else:
            return format_html(
                f'<span style="color: #dc3545; font-weight: bold;">{count} conflicts</span>'
            )
    conflict_count.short_description = "Conflict Status"
    
    def conflict_status(self, obj):
        """Display conflict status badge."""
        from django.db.models import Q
        conflicts = TimetableConflict.objects.filter(
            Q(slot_a=obj) | Q(slot_b=obj)
        ).count()
        
        if conflicts == 0:
            return format_html(
                '<span style="background-color: #198754; color: white; '
                'padding: 3px 8px; border-radius: 3px;">✓ OK</span>'
            )
        else:
            return format_html(
                f'<span style="background-color: #dc3545; color: white; '
                f'padding: 3px 8px; border-radius: 3px;">⚠ {conflicts}</span>'
            )
    conflict_status.short_description = "Status"


@admin.register(TimetableConflict)
class TimetableConflictAdmin(admin.ModelAdmin):
    """Admin for TimetableConflict model."""
    
    list_display = (
        "id",
        "conflict_type_badge",
        "term",
        "slot_a_info",
        "slot_b_info",
        "created_at"
    )
    list_filter = ("conflict_type", "term", "created_at")
    search_fields = (
        "slot_a__curriculum_unit__unit__code",
        "slot_b__curriculum_unit__unit__code",
        "slot_a__room__code",
        "slot_b__room__code"
    )
    ordering = ("-created_at",)
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "formatted_details"
    )
    date_hierarchy = "created_at"
    
    fieldsets = (
        ("Conflict Information", {
            "fields": ("conflict_type", "term")
        }),
        ("Conflicting Slots", {
            "fields": ("slot_a", "slot_b")
        }),
        ("Details", {
            "fields": ("formatted_details",),
        }),
        ("Timestamps", {
            "fields": ("id", "created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    def conflict_type_badge(self, obj):
        """Display conflict type as color-coded badge."""
        colors = {
            "room": "#0d6efd",
            "lecturer": "#ffc107",
            "program": "#dc3545"
        }
        icons = {
            "room": "🏛",
            "lecturer": "👨‍🏫",
            "program": "📚"
        }
        color = colors.get(obj.conflict_type, "#6c757d")
        icon = icons.get(obj.conflict_type, "")
        
        return format_html(
            f'<span style="background-color: {color}; color: white; '
            f'padding: 5px 10px; border-radius: 3px; font-weight: bold;">'
            f'{icon} {obj.get_conflict_type_display()}</span>'
        )
    conflict_type_badge.short_description = "Type"
    
    def slot_a_info(self, obj):
        """Display info about first conflicting slot."""
        return f"{obj.slot_a.curriculum_unit.unit.code} {obj.slot_a.get_day_of_week_display()}"
    slot_a_info.short_description = "Slot A"
    
    def slot_b_info(self, obj):
        """Display info about second conflicting slot."""
        return f"{obj.slot_b.curriculum_unit.unit.code} {obj.slot_b.get_day_of_week_display()}"
    slot_b_info.short_description = "Slot B"
    
    def formatted_details(self, obj):
        """Display conflict details as formatted HTML."""
        import json
        if not obj.details:
            return "No details"
        
        try:
            details = obj.details
            html = "<dl style='margin: 0;'>"
            
            for key, value in details.items():
                if isinstance(value, dict):
                    html += f"<dt><strong>{key}:</strong></dt><dd>"
                    for k, v in value.items():
                        html += f"<div>{k}: {v}</div>"
                    html += "</dd>"
                else:
                    html += f"<dt><strong>{key}:</strong></dt><dd>{value}</dd>"
            
            html += "</dl>"
            return format_html(html)
        except Exception as e:
            return f"Error displaying details: {str(e)}"
    formatted_details.short_description = "Conflict Details"

