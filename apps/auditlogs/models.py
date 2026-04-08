import json
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User


class AuditLog(models.Model):
    """Audit log for tracking important system changes"""
    
    ACTION_CHOICES = [
        ('create', _('Create')),
        ('update', _('Update')),
        ('delete', _('Delete')),
        ('view', _('View')),
        ('login', _('Login')),
        ('logout', _('Logout')),
        ('activate', _('Activate')),
        ('deactivate', _('Deactivate')),
        ('publish', _('Publish')),
        ('export', _('Export')),
        ('import', _('Import')),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        verbose_name=_('User')
    )
    
    action = models.CharField(
        _('Action'),
        max_length=20,
        choices=ACTION_CHOICES
    )
    
    module = models.CharField(
        _('Module'),
        max_length=50,
        help_text=_('Module/Feature where action occurred')
    )
    
    entity_type = models.CharField(
        _('Entity Type'),
        max_length=50,
        help_text=_('Type of object affected (e.g., Student, Course)')
    )
    
    entity_id = models.CharField(
        _('Entity ID'),
        max_length=50,
        blank=True
    )
    
    entity_repr = models.CharField(
        _('Entity Representation'),
        max_length=200,
        blank=True,
        help_text=_('Human-readable representation of the entity')
    )
    
    before_data = models.JSONField(
        _('Before Data'),
        default=dict,
        blank=True,
        help_text=_('Data before the change')
    )
    
    after_data = models.JSONField(
        _('After Data'),
        default=dict,
        blank=True,
        help_text=_('Data after the change')
    )
    
    description = models.TextField(
        _('Description'),
        blank=True
    )
    
    ip_address = models.GenericIPAddressField(
        _('IP Address'),
        null=True,
        blank=True
    )
    
    user_agent = models.TextField(
        _('User Agent'),
        blank=True
    )
    
    created_at = models.DateTimeField(
        _('Created At'),
        auto_now_add=True
    )

    class Meta:
        db_table = 'audit_logs'
        verbose_name = _('Audit Log')
        verbose_name_plural = _('Audit Logs')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['action', '-created_at']),
        ]

    def __str__(self):
        user_str = self.user.get_full_name() if self.user else 'System'
        return f"{user_str} {self.action} {self.entity_type} at {self.created_at}"


class AuditLogMiddleware:
    """Middleware to capture request info for audit logging"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Store IP and user agent in request for later use
        request.audit_ip = self.get_client_ip(request)
        request.audit_user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
