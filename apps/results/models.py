from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.enrollments.models import Enrollment
from apps.core.models import ProcessingStatus


class FinalResult(models.Model):
    """Final computed result for an enrollment"""
    
    enrollment = models.OneToOneField(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='final_result',
        verbose_name=_('Enrollment')
    )
    
    total_score = models.DecimalField(
        _('Total Score'),
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    letter_grade = models.CharField(
        _('Letter Grade'),
        max_length=3,
        blank=True
    )
    
    grade_point = models.DecimalField(
        _('Grade Point'),
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    pass_fail_status = models.CharField(
        _('Pass/Fail Status'),
        max_length=10,
        blank=True
    )
    
    quality_points = models.DecimalField(
        _('Quality Points'),
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Grade Point × Credit Hours')
    )
    
    is_published = models.BooleanField(
        _('Is Published'),
        default=False
    )
    
    published_at = models.DateTimeField(
        _('Published At'),
        null=True,
        blank=True
    )
    
    published_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='published_results',
        verbose_name=_('Published By')
    )
    
    remarks = models.TextField(
        _('Remarks'),
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'final_results'
        verbose_name = _('Final Result')
        verbose_name_plural = _('Final Results')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.enrollment} - {self.letter_grade}"
    
    @property
    def is_passing(self):
        """Check if result is passing"""
        return self.pass_fail_status == 'pass'
    
    def publish(self, triggered_by=None):
        """
        Publish the result through the academic pipeline.
        
        This method should be used instead of directly setting is_published=True
        to ensure the complete pipeline runs.
        
        Args:
            triggered_by: User who is publishing the result
            
        Returns:
            Dict with pipeline processing results
        """
        from apps.core.academic_services import AcademicPipelineService
        return AcademicPipelineService.process_result_publish(self, triggered_by)
    
    def get_processing_status(self):
        """Get the processing status for this result"""
        return ProcessingStatus.get_status(
            ProcessingStatus.PROCESS_RESULT,
            enrollment=self.enrollment,
            student=self.enrollment.student,
            semester=self.enrollment.course_offering.semester,
            course_offering=self.enrollment.course_offering
        )
    
    def update_processing_status(self, status, message=None, details=None, error_message=None, triggered_by=None):
        """Update the processing status for this result"""
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
        
        # Update processing status based on result state
        if is_new:
            # New result created
            if self.total_score is not None:
                self.update_processing_status(
                    ProcessingStatus.STATUS_COMPLETED,
                    message="Result calculated successfully",
                    details={'total_score': str(self.total_score)}
                )
            else:
                self.update_processing_status(
                    ProcessingStatus.STATUS_DRAFT,
                    message="Result created but not yet calculated"
                )
        else:
            # Existing result updated
            if self.is_published:
                self.update_processing_status(
                    ProcessingStatus.STATUS_PUBLISHED,
                    message="Result published",
                    details={'published_by': self.published_by.username if self.published_by else None}
                )
            elif self.total_score is not None:
                self.update_processing_status(
                    ProcessingStatus.STATUS_COMPLETED,
                    message="Result updated",
                    details={'total_score': str(self.total_score)}
                )


class GradeScheme(models.Model):
    """Grade letter to grade point mapping scheme"""
    
    name = models.CharField(
        _('Scheme Name'),
        max_length=100
    )
    
    is_default = models.BooleanField(
        _('Is Default'),
        default=False
    )
    
    description = models.TextField(
        _('Description'),
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'grade_schemes'
        verbose_name = _('Grade Scheme')
        verbose_name_plural = _('Grade Schemes')

    def __str__(self):
        return self.name


class GradeMapping(models.Model):
    """Individual grade mapping within a scheme"""
    
    scheme = models.ForeignKey(
        GradeScheme,
        on_delete=models.CASCADE,
        related_name='mappings',
        verbose_name=_('Grade Scheme')
    )
    
    letter_grade = models.CharField(
        _('Letter Grade'),
        max_length=3
    )
    
    grade_point = models.DecimalField(
        _('Grade Point'),
        max_digits=3,
        decimal_places=2
    )
    
    min_percentage = models.DecimalField(
        _('Minimum Percentage'),
        max_digits=5,
        decimal_places=2
    )
    
    max_percentage = models.DecimalField(
        _('Maximum Percentage'),
        max_digits=5,
        decimal_places=2
    )
    
    is_passing = models.BooleanField(
        _('Is Passing Grade'),
        default=True
    )
    
    order = models.PositiveSmallIntegerField(
        _('Order'),
        default=0
    )

    class Meta:
        db_table = 'grade_mappings'
        verbose_name = _('Grade Mapping')
        verbose_name_plural = _('Grade Mappings')
        ordering = ['-order']

    def __str__(self):
        return f"{self.letter_grade} ({self.min_percentage}-{self.max_percentage}%) = {self.grade_point}"
