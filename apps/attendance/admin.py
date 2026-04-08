from django.contrib import admin
from .models import AttendanceRecord


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'attendance_date', 'status', 'recorded_by', 'recorded_at']
    list_filter = ['status', 'attendance_date']
    search_fields = ['enrollment__student__student_no', 'enrollment__student__user__full_name_en']
    raw_id_fields = ['enrollment', 'recorded_by']
    date_hierarchy = 'attendance_date'
