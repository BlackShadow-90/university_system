from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

from apps.students.models import Student
from apps.courses.offering_models import CourseOffering
from apps.core.models import ProcessingStatus


class Enrollment(models.Model):
    """Student enrollment in a course offering"""
    
    STATUS_CHOICES = [
        ('enrolled', _('Enrolled')),
        ('waiting', _('Waiting List')),
        ('dropped', _('Dropped')),
        ('withdrawn', _('Withdrawn')),
        ('completed', _('Completed')),
    ]
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name=_('Student')
    )
    
    course_offering = models.ForeignKey(
        CourseOffering,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name=_('Course Offering')
    )
    
    enroll_status = models.CharField(
        _('Enrollment Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='enrolled'
    )
    
    enrolled_at = models.DateTimeField(
        _('Enrolled At'),
        auto_now_add=True
    )
    
    dropped_at = models.DateTimeField(
        _('Dropped At'),
        null=True,
        blank=True
    )
    
    drop_reason = models.TextField(
        _('Drop Reason'),
        blank=True
    )
    
    # Attendance tracking
    total_classes = models.PositiveIntegerField(
        _('Total Classes'),
        default=0
    )
    
    attended_classes = models.DecimalField(
        _('Attended Classes'),
        max_digits=6,
        decimal_places=1,
        default=0
    )
    
    attendance_percentage = models.DecimalField(
        _('Attendance Percentage'),
        max_digits=5,
        decimal_places=2,
        default=0.00
    )
    
    # Grade tracking - These are now proxied to FinalResult
    # DO NOT ACCESS DIRECTLY - Use the property methods below
    _final_score = models.DecimalField(
        _('Final Score (Deprecated)'),
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        db_column='final_score'
    )
    
    _letter_grade = models.CharField(
        _('Letter Grade (Deprecated)'),
        max_length=3,
        blank=True,
        db_column='letter_grade'
    )
    
    _grade_point = models.DecimalField(
        _('Grade Point (Deprecated)'),
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        db_column='grade_point'
    )
    
    _pass_fail_status = models.CharField(
        _('Pass/Fail Status (Deprecated)'),
        max_length=10,
        blank=True,
        db_column='pass_fail_status'
    )
    
    result_status = models.CharField(
        _('Result Status'),
        max_length=20,
        choices=[
            ('pending', _('Pending')),
            ('draft', _('Draft')),
            ('published', _('Published')),
        ],
        default='pending'
    )
    
    remarks = models.TextField(
        _('Remarks'),
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'enrollments'
        verbose_name = _('Enrollment')
        verbose_name_plural = _('Enrollments')
        unique_together = ['student', 'course_offering']
        ordering = ['-enrolled_at']

    def __str__(self):
        return f"{self.student.student_no} - {self.course_offering}"
    
    # Properties that proxy to FinalResult
    @property
    def final_score(self):
        """Get final score from FinalResult (single source of truth)"""
        if hasattr(self, 'final_result') and self.final_result:
            return self.final_result.total_score
        return self._final_score
    
    @property
    def letter_grade(self):
        """Get letter grade from FinalResult (single source of truth)"""
        if hasattr(self, 'final_result') and self.final_result:
            return self.final_result.letter_grade
        return self._letter_grade
    
    @property
    def grade_point(self):
        """Get grade point from FinalResult (single source of truth)"""
        if hasattr(self, 'final_result') and self.final_result:
            return self.final_result.grade_point
        return self._grade_point
    
    @property
    def pass_fail_status(self):
        """Get pass/fail status from FinalResult (single source of truth)"""
        if hasattr(self, 'final_result') and self.final_result:
            return self.final_result.pass_fail_status
        return self._pass_fail_status
    
    @property
    def quality_points(self):
        """Get quality points from FinalResult"""
        if hasattr(self, 'final_result') and self.final_result:
            return self.final_result.quality_points
        return None
    
    @property
    def is_result_published(self):
        """Check if final result is published"""
        if hasattr(self, 'final_result') and self.final_result:
            return self.final_result.is_published
        return False
    
    def update_attendance_percentage(self):
        """Calculate and update attendance percentage"""
        from decimal import Decimal
        
        if self.total_classes > 0:
            self.attendance_percentage = (
                Decimal(str(self.attended_classes)) / Decimal(str(self.total_classes)) * Decimal('100')
            )
        else:
            self.attendance_percentage = Decimal('0')
        self.save(update_fields=['attendance_percentage'])
    
    def calculate_final_grade(self):
        """
        Calculate final grade and store in FinalResult (single source of truth).
        This method is deprecated - use FinalResultCalculationService instead.
        """
        from apps.core.academic_services import (
            FinalScoreCalculationService,
            GradeScale,
            FinalResultCalculationService
        )
        
        # Use the hardened pipeline to create/update FinalResult
        try:
            final_result = FinalResultCalculationService.calculate_and_create_final_result(self)
            return {
                'final_score': final_result.total_score,
                'letter_grade': final_result.letter_grade,
                'grade_point': final_result.grade_point,
                'quality_points': final_result.quality_points
            }
        except Exception:
            # Fallback to old behavior if pipeline fails
            final_score = FinalScoreCalculationService.calculate_weighted_score(self)
            grade_scale = GradeScale()
            letter_grade, grade_point = grade_scale.get_grade_for_percentage(final_score)
            return {
                'final_score': final_score,
                'letter_grade': letter_grade,
                'grade_point': grade_point,
                'quality_points': None
            }
    
    @property
    def is_passing(self):
        """Check if student is passing the course using FinalResult"""
        if hasattr(self, 'final_result') and self.final_result:
            return self.final_result.pass_fail_status == 'pass'
        return self._pass_fail_status == 'pass' if self._pass_fail_status else None
    
    def get_attendance_processing_status(self):
        """Get the processing status for attendance tracking"""
        return ProcessingStatus.get_status(
            ProcessingStatus.PROCESS_ATTENDANCE,
            enrollment=self,
            student=self.student,
            semester=self.course_offering.semester,
            course_offering=self.course_offering
        )
    
    def update_attendance_processing_status(self, status, message=None, details=None, error_message=None, triggered_by=None):
        """Update the processing status for attendance tracking"""
        proc_status = self.get_attendance_processing_status()
        proc_status.update_status(status, message, details, error_message, triggered_by)
        return proc_status
    
    @property
    def attendance_processing_status(self):
        """Get the current attendance processing status"""
        return self.get_attendance_processing_status().status
    
    @property
    def attendance_processing_status_display(self):
        """Get the display name of the current attendance processing status"""
        return self.get_attendance_processing_status().get_status_display()
    
    def recalculate_attendance_stats(self):
        """
        Safely recalculate attendance stats from all attendance records.
        This should be called after save, delete, or bulk updates.
        """
        from apps.attendance.models import AttendanceRecord
        from decimal import Decimal
        
        # Get all attendance records for this enrollment
        records = AttendanceRecord.objects.filter(enrollment=self)
        
        total = records.count()
        
        # Count attended classes (present, late, excused, medical, official all count as attended)
        # Only 'absent' is considered not attended
        attended = records.exclude(status='absent').count()
        
        self.total_classes = total
        self.attended_classes = Decimal(str(attended))
        
        if total > 0:
            self.attendance_percentage = (Decimal(str(attended)) / Decimal(str(total)) * Decimal('100'))
        else:
            self.attendance_percentage = Decimal('0')
        
        self.save(update_fields=['total_classes', 'attended_classes', 'attendance_percentage'])
        
        # Update processing status based on attendance state
        if total == 0:
            self.update_attendance_processing_status(
                ProcessingStatus.STATUS_NOT_STARTED,
                message="No attendance records yet",
                details={'total_records': 0}
            )
        elif self.attendance_percentage >= 75:
            self.update_attendance_processing_status(
                ProcessingStatus.STATUS_COMPLETED,
                message="Attendance tracking complete",
                details={
                    'total_classes': total,
                    'attended_classes': str(attended),
                    'percentage': str(self.attendance_percentage)
                }
            )
        elif self.attendance_percentage >= 50:
            self.update_attendance_processing_status(
                ProcessingStatus.STATUS_PARTIAL,
                message="Attendance tracking partial",
                details={
                    'total_classes': total,
                    'attended_classes': str(attended),
                    'percentage': str(self.attendance_percentage)
                }
            )
        else:
            self.update_attendance_processing_status(
                ProcessingStatus.STATUS_FAILED,
                message="Poor attendance",
                details={
                    'total_classes': total,
                    'attended_classes': str(attended),
                    'percentage': str(self.attendance_percentage)
                }
            )
