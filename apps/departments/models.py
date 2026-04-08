from django.db import models
from django.utils.translation import gettext_lazy as _


class Department(models.Model):
    """Department model with bilingual support"""
    
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('inactive', _('Inactive')),
    ]
    
    name_en = models.CharField(_('Department Name (English)'), max_length=100)
    name_zh = models.CharField(_('Department Name (Chinese)'), max_length=100, blank=True)
    code = models.CharField(_('Department Code'), max_length=20, unique=True)
    description_en = models.TextField(_('Description (English)'), blank=True)
    description_zh = models.TextField(_('Description (Chinese)'), blank=True)
    status = models.CharField(
        _('Status'), 
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='active'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'departments'
        verbose_name = _('Department')
        verbose_name_plural = _('Departments')
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name_en}"
    
    def get_name(self, language='en'):
        """Get department name based on language preference"""
        if language == 'zh' and self.name_zh:
            return self.name_zh
        return self.name_en
