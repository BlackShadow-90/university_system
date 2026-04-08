from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache


class SystemSetting(models.Model):
    """System-wide configurable settings"""
    
    DATA_TYPE_CHOICES = [
        ('string', _('String')),
        ('integer', _('Integer')),
        ('decimal', _('Decimal')),
        ('boolean', _('Boolean')),
        ('json', _('JSON')),
        ('text', _('Text')),
    ]
    
    setting_key = models.CharField(
        _('Setting Key'),
        max_length=100,
        unique=True
    )
    
    setting_value = models.TextField(
        _('Setting Value')
    )
    
    data_type = models.CharField(
        _('Data Type'),
        max_length=20,
        choices=DATA_TYPE_CHOICES,
        default='string'
    )
    
    description = models.TextField(
        _('Description'),
        blank=True
    )
    
    is_editable = models.BooleanField(
        _('Is Editable'),
        default=True
    )
    
    category = models.CharField(
        _('Category'),
        max_length=50,
        default='general',
        help_text=_('e.g., general, academic, grading, email')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'system_settings'
        verbose_name = _('System Setting')
        verbose_name_plural = _('System Settings')
        ordering = ['category', 'setting_key']

    def __str__(self):
        return f"{self.setting_key} = {self.setting_value[:50]}"
    
    def get_typed_value(self):
        """Convert stored value to appropriate type"""
        import json
        
        if self.data_type == 'boolean':
            return self.setting_value.lower() in ('true', '1', 'yes', 'on')
        elif self.data_type == 'integer':
            return int(self.setting_value)
        elif self.data_type == 'decimal':
            return float(self.setting_value)
        elif self.data_type == 'json':
            try:
                return json.loads(self.setting_value)
            except json.JSONDecodeError:
                return {}
        else:
            return self.setting_value
    
    def save(self, *args, **kwargs):
        """Clear cache when setting is updated"""
        super().save(*args, **kwargs)
        cache.delete(f'setting_{self.setting_key}')
    
    @classmethod
    def get_value(cls, key, default=None):
        """Get setting value with caching"""
        cached = cache.get(f'setting_{key}')
        if cached is not None:
            return cached
        
        try:
            setting = cls.objects.get(setting_key=key)
            value = setting.get_typed_value()
            cache.set(f'setting_{key}', value, 3600)  # 1 hour cache
            return value
        except cls.DoesNotExist:
            return default
    
    @classmethod
    def set_value(cls, key, value, data_type='string', description=''):
        """Set or create a setting value"""
        import json
        
        if data_type == 'json':
            str_value = json.dumps(value)
        else:
            str_value = str(value)
        
        setting, created = cls.objects.update_or_create(
            setting_key=key,
            defaults={
                'setting_value': str_value,
                'data_type': data_type,
                'description': description,
            }
        )
        return setting


class GradePolicy(models.Model):
    """Grade policy configuration for the institution"""
    
    name = models.CharField(
        _('Policy Name'),
        max_length=100
    )
    
    is_default = models.BooleanField(
        _('Is Default'),
        default=False
    )
    
    # GPA calculation settings
    max_gpa = models.DecimalField(
        _('Maximum GPA'),
        max_digits=3,
        decimal_places=2,
        default=4.00
    )
    
    # Passing thresholds
    passing_grade_point = models.DecimalField(
        _('Minimum Passing Grade Point'),
        max_digits=3,
        decimal_places=2,
        default=1.00
    )
    
    # Warning thresholds
    gpa_warning_threshold = models.DecimalField(
        _('GPA Warning Threshold'),
        max_digits=3,
        decimal_places=2,
        default=2.00
    )
    
    cgpa_warning_threshold = models.DecimalField(
        _('CGPA Warning Threshold'),
        max_digits=3,
        decimal_places=2,
        default=2.00
    )
    
    attendance_warning_threshold = models.DecimalField(
        _('Attendance Warning Threshold (%)'),
        max_digits=5,
        decimal_places=2,
        default=75.00
    )
    
    # Grade point drop warning
    gpa_drop_warning_threshold = models.DecimalField(
        _('GPA Drop Warning Threshold'),
        max_digits=3,
        decimal_places=2,
        default=0.80
    )
    
    description = models.TextField(
        _('Description'),
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'grade_policies'
        verbose_name = _('Grade Policy')
        verbose_name_plural = _('Grade Policies')

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Ensure only one default policy exists"""
        if self.is_default:
            GradePolicy.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)
