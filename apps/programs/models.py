from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.departments.models import Department


class Program(models.Model):
    """Program/Major model with bilingual support"""
    
    DEGREE_CHOICES = [
        ('bachelor', _('Bachelor')),
        ('master', _('Master')),
        ('phd', _('PhD')),
        ('diploma', _('Diploma')),
        ('certificate', _('Certificate')),
    ]
    
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('inactive', _('Inactive')),
    ]
    
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name='programs',
        verbose_name=_('Department')
    )
    
    name_en = models.CharField(_('Program Name (English)'), max_length=100)
    name_zh = models.CharField(_('Program Name (Chinese)'), max_length=100, blank=True)
    code = models.CharField(_('Program Code'), max_length=20, unique=True)
    degree_level = models.CharField(
        _('Degree Level'),
        max_length=20,
        choices=DEGREE_CHOICES,
        default='bachelor'
    )
    duration_years = models.PositiveSmallIntegerField(
        _('Duration (Years)'),
        default=4
    )
    total_credits = models.PositiveSmallIntegerField(
        _('Total Credits Required'),
        default=120
    )
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
        db_table = 'programs'
        verbose_name = _('Program')
        verbose_name_plural = _('Programs')
        ordering = ['department', 'code']

    def __str__(self):
        return f"{self.code} - {self.name_en}"
    
    def get_name(self, language='en'):
        """Get program name based on language preference"""
        if language == 'zh' and self.name_zh:
            return self.name_zh
        return self.name_en
