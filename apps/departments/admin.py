from django.contrib import admin
from .models import Department


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['code', 'name_en', 'name_zh', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['code', 'name_en', 'name_zh']
