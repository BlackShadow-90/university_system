from django.db import models
from django.utils.translation import gettext_lazy as _
import json

from apps.students.models import Student
from apps.semesters.models import Semester
from apps.core.models import ProcessingStatus


# Import extended models to ensure they are registered with Django
from .extended_models import (
    WarningIntervention,
    WarningHistory,
    WarningEvidence,
    WarningEscalationRule,
    WarningResolution,
)


class EarlyWarningRule(models.Model):
    """Configurable rules for early warning system"""
    
    CATEGORY_CHOICES = [
        ('attendance', _('Attendance')),
        ('gpa', _('GPA')),
        ('cgpa', _('CGPA')),
        ('course_failures', _('Course Failures')),
        ('missing_assessment', _('Missing Assessment')),
        ('gpa_trend', _('GPA Trend')),
        ('teacher_flag', _('Teacher Flag')),
    ]
    
    SEVERITY_CHOICES = [
        ('yellow', _('Yellow - Mild')),
        ('orange', _('Orange - Serious')),
        ('red', _('Red - Critical')),
    ]
    
    code = models.CharField(
        _('Rule Code'),
        max_length=50,
        unique=True
    )
    
    name = models.CharField(
        _('Rule Name'),
        max_length=100
    )
    
    description = models.TextField(
        _('Description'),
        blank=True
    )
    
    category = models.CharField(
        _('Category'),
        max_length=30,
        choices=CATEGORY_CHOICES
    )
    
    threshold_value = models.DecimalField(
        _('Threshold Value'),
        max_digits=6,
        decimal_places=2,
        help_text=_('Threshold value for triggering this rule')
    )
    
    comparison_operator = models.CharField(
        _('Comparison'),
        max_length=10,
        default='<',
        help_text=_('Comparison operator: <, >, <=, >=, ==')
    )
    
    weight = models.DecimalField(
        _('Risk Weight'),
        max_digits=4,
        decimal_places=2,
        default=10.00,
        help_text=_('Weight contribution to overall risk score')
    )
    
    severity = models.CharField(
        _('Warning Severity'),
        max_length=10,
        choices=SEVERITY_CHOICES,
        default='yellow'
    )
    
    is_active = models.BooleanField(
        _('Is Active'),
        default=True
    )
    
    order = models.PositiveSmallIntegerField(
        _('Evaluation Order'),
        default=0
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'early_warning_rules'
        verbose_name = _('Early Warning Rule')
        verbose_name_plural = _('Early Warning Rules')
        ordering = ['order', 'category']

    def __str__(self):
        return f"{self.name} ({self.category})"


class EarlyWarningResult(models.Model):
    """Computed early warning result for a student in a semester"""
    
    WARNING_LEVEL_CHOICES = [
        ('green', _('Green - Stable')),
        ('yellow', _('Yellow - Mild Warning')),
        ('orange', _('Orange - Serious Warning')),
        ('red', _('Red - Critical Warning')),
    ]
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='warning_results',
        verbose_name=_('Student')
    )
    
    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        related_name='warning_results',
        verbose_name=_('Semester')
    )
    
    risk_score = models.DecimalField(
        _('Overall Risk Score'),
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text=_('0-100 scale, higher is more at risk')
    )
    
    warning_level = models.CharField(
        _('Warning Level'),
        max_length=20,
        choices=WARNING_LEVEL_CHOICES,
        default='green'
    )
    
    risk_factors = models.JSONField(
        _('Risk Factors'),
        default=list,
        blank=True,
        help_text=_('List of triggered risk factors with details')
    )
    
    attendance_risk_score = models.DecimalField(
        _('Attendance Risk Score'),
        max_digits=5,
        decimal_places=2,
        default=0.00
    )
    
    gpa_risk_score = models.DecimalField(
        _('GPA Risk Score'),
        max_digits=5,
        decimal_places=2,
        default=0.00
    )
    
    cgpa_risk_score = models.DecimalField(
        _('CGPA Risk Score'),
        max_digits=5,
        decimal_places=2,
        default=0.00
    )
    
    course_failure_risk_score = models.DecimalField(
        _('Course Failure Risk Score'),
        max_digits=5,
        decimal_places=2,
        default=0.00
    )
    
    trend_risk_score = models.DecimalField(
        _('Trend Risk Score'),
        max_digits=5,
        decimal_places=2,
        default=0.00
    )
    
    missing_assessment_risk_score = models.DecimalField(
        _('Missing Assessment Risk Score'),
        max_digits=5,
        decimal_places=2,
        default=0.00
    )
    
    teacher_flag_risk_score = models.DecimalField(
        _('Teacher Flag Risk Score'),
        max_digits=5,
        decimal_places=2,
        default=0.00
    )
    
    recommendations = models.JSONField(
        _('Recommendations'),
        default=list,
        blank=True,
        help_text=_('List of suggested interventions')
    )
    
    is_acknowledged = models.BooleanField(
        _('Is Acknowledged by Student'),
        default=False
    )
    
    acknowledged_at = models.DateTimeField(
        _('Acknowledged At'),
        null=True,
        blank=True
    )
    
    generated_at = models.DateTimeField(
        _('Generated At'),
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'early_warning_results'
        verbose_name = _('Early Warning Result')
        verbose_name_plural = _('Early Warning Results')
        unique_together = ['student', 'semester']
        ordering = ['-generated_at']

    def __str__(self):
        return f"{self.student.student_no} - {self.semester} - {self.get_warning_level_display()}"
    
    def get_risk_factors_list(self):
        """Return risk factors as list of strings"""
        if isinstance(self.risk_factors, list):
            return self.risk_factors
        try:
            return json.loads(self.risk_factors) if self.risk_factors else []
        except (json.JSONDecodeError, TypeError):
            return []
    
    def get_recommendations_list(self):
        """Return recommendations as list of strings"""
        if isinstance(self.recommendations, list):
            return self.recommendations
        try:
            return json.loads(self.recommendations) if self.recommendations else []
        except (json.JSONDecodeError, TypeError):
            return []
    
    def get_processing_status(self):
        """Get the processing status for this warning"""
        return ProcessingStatus.get_status(
            ProcessingStatus.PROCESS_WARNING,
            student=self.student,
            semester=self.semester
        )
    
    def update_processing_status(self, status, message=None, details=None, error_message=None, triggered_by=None):
        """Update the processing status for this warning"""
        proc_status = self.get_processing_status()
        proc_status.update_status(status, message, details, error_message, triggered_by)
        return proc_status
    
    @property
    def processing_status(self):
        """Get the current processing status"""
        return self.get_processing_status().status
    
    @property
    def processing_status_display(self):
        """Get the display name of the current processing status"""
        return self.get_processing_status().get_status_display()
    
    def save(self, *args, **kwargs):
        """Override save to update processing status"""
        is_new = self.pk is None
        
        super().save(*args, **kwargs)
        
        # Update processing status based on warning state
        if is_new:
            # New warning generated
            self.update_processing_status(
                ProcessingStatus.STATUS_COMPLETED,
                message="Warning generated successfully",
                details={
                    'warning_level': self.warning_level,
                    'attendance_risk': str(self.attendance_risk_score),
                    'gpa_risk': str(self.gpa_risk_score)
                }
            )
        else:
            # Existing warning updated
            self.update_processing_status(
                ProcessingStatus.STATUS_COMPLETED,
                message="Warning updated",
                details={
                    'warning_level': self.warning_level,
                    'acknowledged': self.is_acknowledged
                }
            )
