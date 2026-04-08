from django.contrib import admin
from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title_en', 'priority', 'target_role', 'is_pinned', 'is_active', 'published_at', 'view_count']
    list_filter = ['priority', 'target_role', 'is_pinned', 'is_active', 'published_at']
    search_fields = ['title_en', 'title_zh', 'content_en', 'content_zh']
    raw_id_fields = ['published_by']
