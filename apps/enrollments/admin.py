from django.contrib import admin
from .models import Enrollment


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course_offering', 'enroll_status', 'attendance_percentage', 'letter_grade', 'enrolled_at']
    list_filter = ['enroll_status', 'course_offering__semester']
    search_fields = ['student__student_no', 'student__user__full_name_en']
    raw_id_fields = ['student', 'course_offering']
    date_hierarchy = 'enrolled_at'
