from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

from apps.courses.offering_models import CourseOffering


class AssessmentComponent(models.Model):
    """Assessment component for a course (e.g., midterm, final, assignment)"""
    
    TYPE_CHOICES = [
        ('attendance', _('Attendance')),
        ('assignment', _('Assignment')),
        ('quiz', _('Quiz')),
        ('midterm', _('Midterm Exam')),
        ('lab', _('Lab Work')),
        ('project', _('Project')),
        ('presentation', _('Presentation')),
        ('final', _('Final Exam')),
        ('participation', _('Participation')),
        ('other', _('Other')),
    ]
    
    course_offering = models.ForeignKey(
        CourseOffering,
        on_delete=models.CASCADE,
        related_name='assessment_components',
        verbose_name=_('Course Offering')
    )
    
    name = models.CharField(
        _('Component Name'),
        max_length=100
    )
    
    assessment_type = models.CharField(
        _('Assessment Type'),
        max_length=20,
        choices=TYPE_CHOICES,
        default='assignment'
    )
    
    weight_percentage = models.DecimalField(
        _('Weight (%)'),
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_('Percentage weight towards final grade')
    )
    
    max_score = models.DecimalField(
        _('Maximum Score'),
        max_digits=6,
        decimal_places=2,
        default=100.00,
        validators=[MinValueValidator(0)]
    )
    
    due_date = models.DateField(
        _('Due Date'),
        null=True,
        blank=True
    )
    
    description = models.TextField(
        _('Description'),
        blank=True
    )
    
    is_published = models.BooleanField(
        _('Scores Published'),
        default=False
    )
    
    order = models.PositiveSmallIntegerField(
        _('Display Order'),
        default=0
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'assessment_components'
        verbose_name = _('Assessment Component')
        verbose_name_plural = _('Assessment Components')
        ordering = ['order', 'id']

    @property
    def is_exam(self):
        """Check if this is an exam type assessment"""
        return self.assessment_type in ['midterm', 'final']
    
    def clean(self):
        """Validate component data before saving."""
        from django.core.exceptions import ValidationError
        from django.db.models import Sum
        
        # Validate weight doesn't exceed 100% when combined with other components
        if self.pk:
            # Existing component - exclude self from calculation
            other_weights = self.course_offering.assessment_components.exclude(
                pk=self.pk
            ).aggregate(total=Sum('weight_percentage'))['total'] or 0
        else:
            # New component
            other_weights = self.course_offering.assessment_components.aggregate(
                total=Sum('weight_percentage')
            )['total'] or 0
        
        total_weight = other_weights + self.weight_percentage
        
        if total_weight > 100:
            raise ValidationError({
                'weight_percentage': f'Total weight would exceed 100%. Current others: {other_weights}%'
            })
        
        super().clean()


class AssessmentScore(models.Model):
    """Individual student score for an assessment component"""
    
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('submitted', _('Submitted')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
    ]
    
    enrollment = models.ForeignKey(
        'enrollments.Enrollment',
        on_delete=models.CASCADE,
        related_name='assessment_scores',
        verbose_name=_('Enrollment')
    )
    
    assessment_component = models.ForeignKey(
        AssessmentComponent,
        on_delete=models.CASCADE,
        related_name='scores',
        verbose_name=_('Assessment Component')
    )
    
    score = models.DecimalField(
        _('Score'),
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        null=True,
        blank=True
    )
    
    percentage = models.DecimalField(
        _('Percentage'),
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    remarks = models.TextField(
        _('Remarks'),
        blank=True
    )
    
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    
    entered_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='entered_scores',
        verbose_name=_('Entered By')
    )
    
    entered_at = models.DateTimeField(
        _('Entered At'),
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'assessment_scores'
        verbose_name = _('Assessment Score')
        verbose_name_plural = _('Assessment Scores')
        unique_together = ['enrollment', 'assessment_component']
        ordering = ['assessment_component__order']

    def __str__(self):
        return f"{self.enrollment.student.student_no} - {self.assessment_component.name}: {self.score}"
    
    def calculate_percentage(self):
        """Calculate percentage based on max score"""
        if self.score is not None and self.assessment_component.max_score > 0:
            # Convert to Decimal for consistent arithmetic
            from decimal import Decimal
            max_score = Decimal(str(self.assessment_component.max_score))
            self.percentage = (self.score / max_score) * Decimal('100')
        return self.percentage
    
    def save(self, *args, **kwargs):
        """Auto-calculate percentage and trigger academic pipeline"""
        self.full_clean()
        self.calculate_percentage()
        
        # Get current user (should be set via set_request_user() before save)
        current_user = getattr(self, '_request_user', None)
        
        # Save the score first
        super().save(*args, **kwargs)
        
        # Trigger academic pipeline for mark updates
        if self.score is not None:
            from apps.core.academic_services import AcademicPipelineService
            try:
                AcademicPipelineService.process_mark_update(self, triggered_by=current_user)
            except Exception as e:
                # Log error but don't fail the save
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to process academic pipeline for score update: {e}")
    
    def set_request_user(self, user):
        """Helper to set request user for pipeline processing"""
        self._request_user = user
