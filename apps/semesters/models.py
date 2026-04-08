from django.db import models
from django.utils.translation import gettext_lazy as _


class Semester(models.Model):
    """Academic Semester model"""
    
    SEMESTER_CHOICES = [
        ('fall', _('Fall Semester')),
        ('spring', _('Spring Semester')),
        ('summer', _('Summer Semester')),
        ('winter', _('Winter Semester')),
    ]
    
    STATUS_CHOICES = [
        ('upcoming', _('Upcoming')),
        ('active', _('Active')),
        ('completed', _('Completed')),
        ('archived', _('Archived')),
    ]
    
    academic_year = models.CharField(_('Academic Year'), max_length=20)
    semester_type = models.CharField(
        _('Semester Type'),
        max_length=20,
        choices=SEMESTER_CHOICES,
        default='fall'
    )
    name_en = models.CharField(_('Name (English)'), max_length=50)
    name_zh = models.CharField(_('Name (Chinese)'), max_length=50, blank=True)
    start_date = models.DateField(_('Start Date'))
    end_date = models.DateField(_('End Date'))
    registration_start = models.DateField(_('Registration Start'), null=True, blank=True)
    registration_end = models.DateField(_('Registration End'), null=True, blank=True)
    grade_entry_start = models.DateField(_('Grade Entry Start'), null=True, blank=True)
    grade_entry_end = models.DateField(_('Grade Entry End'), null=True, blank=True)
    is_active = models.BooleanField(_('Is Active'), default=False)
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='upcoming'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'semesters'
        verbose_name = _('Semester')
        verbose_name_plural = _('Semesters')
        ordering = ['-academic_year', 'semester_type']
        unique_together = ['academic_year', 'semester_type']

    def __str__(self):
        return f"{self.academic_year} {self.get_semester_type_display()}"
    
    def get_name(self, language='en'):
        """Get semester name based on language preference"""
        if language == 'zh' and self.name_zh:
            return self.name_zh
        return self.name_en
    
    @property
    def display_name(self):
        return f"{self.academic_year} {self.get_semester_type_display()}"
    
    def save(self, *args, **kwargs):
        """Auto-generate name if not provided"""
        if not self.name_en:
            self.name_en = f"{self.academic_year} {self.get_semester_type_display()}"
        if not self.name_zh:
            semester_zh = {
                'fall': '秋季学期',
                'spring': '春季学期',
                'summer': '夏季学期',
                'winter': '冬季学期',
            }
            self.name_zh = f"{self.academic_year} {semester_zh.get(self.semester_type, '')}"
        super().save(*args, **kwargs)
