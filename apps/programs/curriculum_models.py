from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.programs.models import Program
from apps.courses.models import Course


class CurriculumCourse(models.Model):
    """Link between Programs and Courses - defines curriculum structure"""
    
    COURSE_NATURE_CHOICES = [
        ('required', _('Required')),
        ('elective', _('Elective')),
        ('optional', _('Optional')),
    ]
    
    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
        related_name='curriculum_courses',
        verbose_name=_('Program')
    )
    
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='program_curricula',
        verbose_name=_('Course')
    )
    
    recommended_semester = models.PositiveSmallIntegerField(
        _('Recommended Semester'),
        help_text=_('The semester this course is recommended for (1, 2, 3, etc.)')
    )
    
    is_required = models.BooleanField(
        _('Is Required'),
        default=True
    )
    
    course_nature = models.CharField(
        _('Course Nature'),
        max_length=20,
        choices=COURSE_NATURE_CHOICES,
        default='required'
    )
    
    notes = models.TextField(_('Notes'), blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'curriculum_courses'
        verbose_name = _('Curriculum Course')
        verbose_name_plural = _('Curriculum Courses')
        unique_together = ['program', 'course']
        ordering = ['program', 'recommended_semester', 'course__code']

    def __str__(self):
        return f"{self.program.code} - {self.course.code} (Sem {self.recommended_semester})"
