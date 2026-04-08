from django.contrib import admin
from .models import Course
from .offering_models import CourseOffering


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'title_en', 'credit_hours', 'course_type', 'department', 'status']
    list_filter = ['status', 'course_type', 'department']
    search_fields = ['code', 'title_en', 'title_zh']
    filter_horizontal = ['prerequisites']


@admin.register(CourseOffering)
class CourseOfferingAdmin(admin.ModelAdmin):
    list_display = ['course', 'semester', 'teacher', 'section_name', 'capacity', 'status']
    list_filter = ['status', 'semester', 'day_of_week']
    search_fields = ['course__code', 'course__title_en', 'teacher__user__full_name_en']
    raw_id_fields = ['course', 'semester', 'teacher']
