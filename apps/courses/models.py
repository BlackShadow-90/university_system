from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

from apps.departments.models import Department


class Course(models.Model):
    """Course model with bilingual support"""
    
    COURSE_TYPE_CHOICES = [
        ('theory', _('Theory')),
        ('lab', _('Laboratory')),
        ('theory_lab', _('Theory + Lab')),
        ('seminar', _('Seminar')),
        ('project', _('Project')),
        ('internship', _('Internship')),
        ('thesis', _('Thesis/Dissertation')),
    ]
    
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('inactive', _('Inactive')),
        ('archived', _('Archived')),
    ]
    
    code = models.CharField(_('Course Code'), max_length=20, unique=True)
    title_en = models.CharField(_('Course Title (English)'), max_length=200)
    title_zh = models.CharField(_('Course Title (Chinese)'), max_length=200, blank=True)
    
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name='courses',
        verbose_name=_('Department')
    )
    
    credit_hours = models.DecimalField(
        _('Credit Hours'),
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(0), MaxValueValidator(20)]
    )
    
    lecture_hours = models.DecimalField(
        _('Lecture Hours per Week'),
        max_digits=3,
        decimal_places=1,
        default=3.0
    )
    
    lab_hours = models.DecimalField(
        _('Lab Hours per Week'),
        max_digits=3,
        decimal_places=1,
        default=0.0
    )
    
    course_type = models.CharField(
        _('Course Type'),
        max_length=20,
        choices=COURSE_TYPE_CHOICES,
        default='theory'
    )
    
    prerequisites = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='is_prerequisite_for',
        verbose_name=_('Prerequisites')
    )
    
    description_en = models.TextField(_('Description (English)'), blank=True)
    description_zh = models.TextField(_('Description (Chinese)'), blank=True)
    
    learning_outcomes_en = models.TextField(_('Learning Outcomes (English)'), blank=True)
    learning_outcomes_zh = models.TextField(_('Learning Outcomes (Chinese)'), blank=True)
    
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'courses'
        verbose_name = _('Course')
        verbose_name_plural = _('Courses')
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.title_en}"
    
    def get_title(self, language='en'):
        """Get course title based on language preference"""
        if language == 'zh' and self.title_zh:
            return self.title_zh
        return self.title_en
    
    def get_description(self, language='en'):
        """Get course description based on language preference"""
        if language == 'zh' and self.description_zh:
            return self.description_zh
        return self.description_en
    
    @property
    def total_hours(self):
        """Return total contact hours per week"""
        return self.lecture_hours + self.lab_hours
