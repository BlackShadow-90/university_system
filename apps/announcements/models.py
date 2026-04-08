from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User


class Announcement(models.Model):
    """System-wide announcements"""
    
    PRIORITY_CHOICES = [
        ('low', _('Low')),
        ('normal', _('Normal')),
        ('high', _('High')),
        ('urgent', _('Urgent')),
    ]
    
    TARGET_ROLE_CHOICES = [
        ('all', _('All Users')),
        ('students', _('Students Only')),
        ('teachers', _('Teachers Only')),
        ('admin', _('Administrators Only')),
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
    
    summary_en = models.TextField(
        _('Summary (English)'),
        blank=True,
        help_text=_('Short summary for preview cards')
    )
    
    summary_zh = models.TextField(
        _('Summary (Chinese)'),
        blank=True
    )
    
    priority = models.CharField(
        _('Priority'),
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='normal'
    )
    
    target_role = models.CharField(
        _('Target Audience'),
        max_length=20,
        choices=TARGET_ROLE_CHOICES,
        default='all'
    )
    
    published_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='published_announcements',
        verbose_name=_('Published By')
    )
    
    published_at = models.DateTimeField(
        _('Published At'),
        null=True,
        blank=True
    )
    
    expires_at = models.DateTimeField(
        _('Expires At'),
        null=True,
        blank=True
    )
    
    is_pinned = models.BooleanField(
        _('Is Pinned'),
        default=False,
        help_text=_('Pin to top of announcements list')
    )
    
    is_active = models.BooleanField(
        _('Is Active'),
        default=True
    )
    
    attachment = models.FileField(
        _('Attachment'),
        upload_to='announcements/%Y/%m/',
        blank=True,
        null=True
    )
    
    view_count = models.PositiveIntegerField(
        _('View Count'),
        default=0
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'announcements'
        verbose_name = _('Announcement')
        verbose_name_plural = _('Announcements')
        ordering = ['-is_pinned', '-published_at', '-created_at']

    def __str__(self):
        return self.title_en[:50]
    
    def get_title(self, language=None):
        """Get title based on language preference"""
        from django.utils.translation import get_language
        if language is None:
            language = get_language()
        # Check for Chinese language codes (zh, zh-hans, zh-hant, etc.)
        if language and language.startswith('zh') and self.title_zh:
            return self.title_zh
        return self.title_en
    
    def get_content(self, language=None):
        """Get content based on language preference"""
        from django.utils.translation import get_language
        if language is None:
            language = get_language()
        # Check for Chinese language codes
        if language and language.startswith('zh') and self.content_zh:
            return self.content_zh
        return self.content_en
    
    def get_summary(self, language=None):
        """Get summary based on language preference"""
        from django.utils.translation import get_language
        if language is None:
            language = get_language()
        # Check for Chinese language codes
        if language and language.startswith('zh'):
            if self.summary_zh:
                return self.summary_zh
        return self.summary_en or self.content_en[:200]
    
    def increment_view_count(self):
        """Increment the view counter"""
        self.view_count += 1
        self.save(update_fields=['view_count'])
