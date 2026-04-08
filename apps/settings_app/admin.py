from django.contrib import admin
from .models import SystemSetting, GradePolicy


@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ['setting_key', 'setting_value', 'data_type', 'category', 'is_editable']
    list_filter = ['data_type', 'category', 'is_editable']
    search_fields = ['setting_key', 'description']


@admin.register(GradePolicy)
class GradePolicyAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_default', 'passing_grade_point', 'gpa_warning_threshold', 'cgpa_warning_threshold']
    list_filter = ['is_default']
