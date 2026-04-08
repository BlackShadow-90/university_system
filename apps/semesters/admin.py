from django.contrib import admin
from .models import Semester


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ['academic_year', 'semester_type', 'name_en', 'start_date', 'end_date', 'is_active', 'status']
    list_filter = ['status', 'is_active', 'semester_type', 'academic_year']
    search_fields = ['academic_year', 'name_en', 'name_zh']
    date_hierarchy = 'start_date'
