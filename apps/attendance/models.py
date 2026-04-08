from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings

from apps.enrollments.models import Enrollment
from apps.accounts.models import User


class AttendanceRecord(models.Model):
    """Daily attendance record for a student in a course"""
    
    STATUS_CHOICES = [
        ('present', _('Present')),
        ('absent', _('Absent')),
        ('late', _('Late')),
        ('excused', _('Excused')),
        ('medical', _('Medical Leave')),
        ('official', _('Official Leave')),
    ]
    
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='attendance_records',
        verbose_name=_('Enrollment')
    )
    
    attendance_date = models.DateField(
        _('Attendance Date')
    )
    
    status = models.CharField(
        _('Attendance Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='present'
    )
    
    remarks = models.TextField(
        _('Remarks'),
        blank=True
    )
    
    recorded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recorded_attendance',
        verbose_name=_('Recorded By')
    )
    
    recorded_at = models.DateTimeField(
        _('Recorded At'),
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'attendance_records'
        verbose_name = _('Attendance Record')
        verbose_name_plural = _('Attendance Records')
        unique_together = ['enrollment', 'attendance_date']
        ordering = ['-attendance_date']

    def clean(self):
        """Validate attendance record before saving."""
        from django.utils import timezone
        
        # Prevent marking future dates
        if self.attendance_date > timezone.now().date():
            raise ValidationError({
                'attendance_date': _('Cannot mark attendance for future dates.')
            })
        
        # Check lock period (default: 7 days)
        lock_days = getattr(settings, 'ATTENDANCE_LOCK_DAYS', 7)
        if not self.pk:  # New record
            return
        
        # For existing records, check if within edit window
        days_since_recorded = (timezone.now().date() - self.recorded_at.date()).days
        if days_since_recorded > lock_days:
            raise ValidationError({
                'attendance_date': _('Attendance records are locked after %(days)d days.') % {'days': lock_days}
            })
        
        super().clean()
    
    @property
    def is_present(self):
        """Check if student was present (counts for attendance)"""
        return self.status in ['present', 'excused', 'medical', 'official']
    
    @property
    def attendance_credit(self):
        """
        Get attendance credit value for this record.
        
        Returns:
            float: 1.0 for full credit, 0.5 for late, 0.0 for absent
        """
        if self.status in ['present', 'excused', 'medical', 'official']:
            return 1.0
        elif self.status == 'late':
            return 0.5
        return 0.0
    
    def save(self, *args, **kwargs):
        """Update enrollment attendance stats and trigger academic pipeline"""
        self.full_clean()
        
        # Get current user (should be set via set_request_user() before save)
        current_user = getattr(self, '_request_user', None)
        
        # Save the attendance record first
        super().save(*args, **kwargs)
        
        # Trigger academic pipeline for attendance updates
        from apps.core.academic_services import AcademicPipelineService
        try:
            AcademicPipelineService.process_attendance_update(self, triggered_by=current_user)
        except Exception as e:
            # Log error but don't fail the save
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to process academic pipeline for attendance update: {e}")
    
    def set_request_user(self, user):
        """Helper to set request user for pipeline processing"""
        self._request_user = user

    def delete(self, *args, **kwargs):
        """Update enrollment attendance stats after deletion"""
        enrollment = self.enrollment
        super().delete(*args, **kwargs)
        
        # Safely recalculate attendance stats from all records
        enrollment.recalculate_attendance_stats()
