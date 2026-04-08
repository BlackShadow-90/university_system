from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User


class Notification(models.Model):
    """System notification for users"""
    
    PRIORITY_CHOICES = [
        ('low', _('Low')),
        ('normal', _('Normal')),
        ('high', _('High')),
        ('urgent', _('Urgent')),
    ]
    
    TYPE_CHOICES = [
        ('system', _('System')),
        ('academic', _('Academic')),
        ('warning', _('Warning')),
        ('grade', _('Grade')),
        ('attendance', _('Attendance')),
        ('message', _('Message')),
        ('announcement', _('Announcement')),
    ]
    
    title_en = models.CharField(
        _('Title (English)'),
        max_length=200
    )
    
    title_zh = models.CharField(
        _('Title (Chinese)'),
        max_length=200,
        blank=True
    )
    
    content_en = models.TextField(
        _('Content (English)')
    )
    
    content_zh = models.TextField(
        _('Content (Chinese)'),
        blank=True
    )
    
    notification_type = models.CharField(
        _('Notification Type'),
        max_length=20,
        choices=TYPE_CHOICES,
        default='system'
    )
    
    priority = models.CharField(
        _('Priority'),
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='normal'
    )
    
    sender = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_notifications',
        verbose_name=_('Sender')
    )
    
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('Recipient')
    )
    
    related_object_type = models.CharField(
        _('Related Object Type'),
        max_length=50,
        blank=True,
        help_text=_('e.g., enrollment, course, warning')
    )
    
    related_object_id = models.PositiveIntegerField(
        _('Related Object ID'),
        null=True,
        blank=True
    )
    
    is_read = models.BooleanField(
        _('Is Read'),
        default=False
    )
    
    read_at = models.DateTimeField(
        _('Read At'),
        null=True,
        blank=True
    )
    
    is_emailed = models.BooleanField(
        _('Email Sent'),
        default=False
    )
    
    emailed_at = models.DateTimeField(
        _('Emailed At'),
        null=True,
        blank=True
    )
    
    action_url = models.URLField(
        _('Action URL'),
        blank=True,
        help_text=_('Optional URL for user to take action')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notifications'
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient.get_full_name()} - {self.title_en[:50]}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            from django.utils import timezone
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    def get_title(self, language='en'):
        """Get title based on language preference"""
        if language == 'zh' and self.title_zh:
            return self.title_zh
        return self.title_en
    
    def get_content(self, language='en'):
        """Get content based on language preference"""
        if language == 'zh' and self.content_zh:
            return self.content_zh
        return self.content_en
