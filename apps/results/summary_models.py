from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.students.models import Student
from apps.semesters.models import Semester


class SemesterSummary(models.Model):
    """Semester summary for a student with GPA and performance metrics"""
    
    WARNING_LEVEL_CHOICES = [
        ('green', _('Green - Stable')),
        ('yellow', _('Yellow - Mild Warning')),
        ('orange', _('Orange - Serious Warning')),
        ('red', _('Red - Critical Warning')),
    ]
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='semester_summaries',
        verbose_name=_('Student')
    )
    
    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        related_name='student_summaries',
        verbose_name=_('Semester')
    )
    
    semester_gpa = models.DecimalField(
        _('Semester GPA'),
        max_digits=3,
        decimal_places=2,
        default=0.00
    )
    
    semester_credits_attempted = models.DecimalField(
        _('Credits Attempted'),
        max_digits=5,
        decimal_places=2,
        default=0.00
    )
    
    semester_credits_earned = models.DecimalField(
        _('Credits Earned'),
        max_digits=5,
        decimal_places=2,
        default=0.00
    )
    
    total_quality_points = models.DecimalField(
        _('Total Quality Points'),
        max_digits=8,
        decimal_places=2,
        default=0.00
    )
    
    courses_attempted = models.PositiveSmallIntegerField(
        _('Courses Attempted'),
        default=0
    )
    
    courses_passed = models.PositiveSmallIntegerField(
        _('Courses Passed'),
        default=0
    )
    
    courses_failed = models.PositiveSmallIntegerField(
        _('Courses Failed'),
        default=0
    )
    
    failed_courses_list = models.JSONField(
        _('Failed Courses List'),
        default=list,
        blank=True
    )
    
    warning_level = models.CharField(
        _('Warning Level'),
        max_length=20,
        choices=WARNING_LEVEL_CHOICES,
        default='green'
    )
    
    computed_at = models.DateTimeField(
        _('Computed At'),
        auto_now=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'semester_summaries'
        verbose_name = _('Semester Summary')
        verbose_name_plural = _('Semester Summaries')
        unique_together = ['student', 'semester']
        ordering = ['-semester__academic_year', 'semester__semester_type']

    def __str__(self):
        return f"{self.student.student_no} - {self.semester} - GPA: {self.semester_gpa}"


class CGPARecord(models.Model):
    """Cumulative GPA record for a student"""
    
    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        related_name='cgpa_record',
        verbose_name=_('Student')
    )
    
    cumulative_gpa = models.DecimalField(
        _('Cumulative GPA'),
        max_digits=3,
        decimal_places=2,
        default=0.00
    )
    
    cumulative_credits_attempted = models.DecimalField(
        _('Total Credits Attempted'),
        max_digits=6,
        decimal_places=2,
        default=0.00
    )
    
    cumulative_credits_earned = models.DecimalField(
        _('Total Credits Earned'),
        max_digits=6,
        decimal_places=2,
        default=0.00
    )
    
    total_quality_points = models.DecimalField(
        _('Total Quality Points'),
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    
    semesters_completed = models.PositiveSmallIntegerField(
        _('Semesters Completed'),
        default=0
    )
    
    computed_at = models.DateTimeField(
        _('Last Computed'),
        auto_now=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cgpa_records'
        verbose_name = _('CGPA Record')
        verbose_name_plural = _('CGPA Records')

    def __str__(self):
        return f"{self.student.student_no} - CGPA: {self.cumulative_gpa}"
    
    def update_from_summaries(self):
        """Update CGPA from all semester summaries"""
        summaries = self.student.semester_summaries.all()
        
        total_credits_attempted = sum(
            s.semester_credits_attempted for s in summaries
        )
        total_credits_earned = sum(
            s.semester_credits_earned for s in summaries
        )
        total_quality_points = sum(
            s.total_quality_points for s in summaries
        )
        
        self.cumulative_credits_attempted = total_credits_attempted
        self.cumulative_credits_earned = total_credits_earned
        self.total_quality_points = total_quality_points
        
        if total_credits_attempted > 0:
            self.cumulative_gpa = total_quality_points / total_credits_attempted
        else:
            self.cumulative_gpa = 0.00
        
        self.semesters_completed = summaries.count()
        self.save()
