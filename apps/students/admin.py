from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_no', 'user', 'department', 'program', 'batch_year', 'status', 'cgpa']
    list_filter = ['status', 'department', 'program', 'batch_year']
    search_fields = ['student_no', 'user__full_name_en', 'user__email']
    raw_id_fields = ['user', 'department', 'program', 'current_semester', 'advisor']
