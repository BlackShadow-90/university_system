from django.contrib import admin
from .models import Program
from .curriculum_models import CurriculumCourse


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ['code', 'name_en', 'department', 'degree_level', 'duration_years', 'status']
    list_filter = ['status', 'degree_level', 'department']
    search_fields = ['code', 'name_en', 'name_zh']
    raw_id_fields = ['department']


@admin.register(CurriculumCourse)
class CurriculumCourseAdmin(admin.ModelAdmin):
    list_display = ['program', 'course', 'recommended_semester', 'is_required']
    list_filter = ['program', 'is_required', 'course_nature']
    raw_id_fields = ['program', 'course']
