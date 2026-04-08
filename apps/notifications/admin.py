from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title_en', 'notification_type', 'priority', 'recipient', 'is_read', 'created_at']
    list_filter = ['notification_type', 'priority', 'is_read', 'is_emailed', 'created_at']
    search_fields = ['title_en', 'recipient__email']
    raw_id_fields = ['sender', 'recipient']
