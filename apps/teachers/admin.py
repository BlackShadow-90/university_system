from django.contrib import admin
from .models import Teacher


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['teacher_no', 'user', 'department', 'title', 'status', 'join_date']
    list_filter = ['status', 'department', 'title']
    search_fields = ['teacher_no', 'user__full_name_en', 'user__email']
    raw_id_fields = ['user', 'department']
