from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
import json
import traceback

User = get_user_model()


class ProcessingStatus(models.Model):
    """
    Tracks processing status for various academic operations.
    Provides a unified way to track the state of results, warnings, and attendance.
    """
    
    # Process types
    PROCESS_RESULT = 'result'
    PROCESS_WARNING = 'warning'
    PROCESS_ATTENDANCE = 'attendance'
    
    PROCESS_TYPES = [
        (PROCESS_RESULT, _('Result Processing')),
        (PROCESS_WARNING, _('Warning Generation')),
        (PROCESS_ATTENDANCE, _('Attendance Tracking')),
    ]
    
    # Status values
    STATUS_NOT_STARTED = 'not_started'
    STATUS_DRAFT = 'draft'
    STATUS_INCOMPLETE = 'incomplete'
    STATUS_READY = 'ready'
    STATUS_PROCESSING = 'processing'
    STATUS_COMPLETED = 'completed'
    STATUS_PUBLISHED = 'published'
    STATUS_FAILED = 'failed'
    STATUS_LOCKED = 'locked'
    STATUS_PARTIAL = 'partial'
    
    STATUS_CHOICES = [
        (STATUS_NOT_STARTED, _('Not Started')),
        (STATUS_DRAFT, _('Draft')),
        (STATUS_INCOMPLETE, _('Incomplete')),
        (STATUS_READY, _('Ready')),
        (STATUS_PROCESSING, _('Processing')),
        (STATUS_COMPLETED, _('Completed')),
        (STATUS_PUBLISHED, _('Published')),
        (STATUS_FAILED, _('Failed')),
        (STATUS_LOCKED, _('Locked')),
        (STATUS_PARTIAL, _('Partial')),
    ]
    
    # Core fields
    process_type = models.CharField(
        _('Process Type'),
        max_length=20,
        choices=PROCESS_TYPES
    )
    
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NOT_STARTED
    )
    
    # Related objects (flexible - can reference any model)
    student_id = models.PositiveIntegerField(
        _('Student ID'),
        null=True,
        blank=True,
        db_index=True
    )
    
    enrollment_id = models.PositiveIntegerField(
        _('Enrollment ID'),
        null=True,
        blank=True,
        db_index=True
    )
    
    semester_id = models.PositiveIntegerField(
        _('Semester ID'),
        null=True,
        blank=True,
        db_index=True
    )
    
    course_offering_id = models.PositiveIntegerField(
        _('Course Offering ID'),
        null=True,
        blank=True,
        db_index=True
    )
    
    # Status details
    message = models.TextField(
        _('Status Message'),
        blank=True
    )
    
    details = models.JSONField(
        _('Status Details'),
        default=dict,
        blank=True
    )
    
    error_message = models.TextField(
        _('Error Message'),
        blank=True
    )
    
    # Metadata
    triggered_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='triggered_processing_statuses'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'processing_statuses'
        verbose_name = _('Processing Status')
        verbose_name_plural = _('Processing Statuses')
        indexes = [
            models.Index(fields=['process_type', 'status']),
            models.Index(fields=['student_id', 'process_type']),
            models.Index(fields=['enrollment_id', 'process_type']),
            models.Index(fields=['semester_id', 'process_type']),
            models.Index(fields=['updated_at']),
        ]
    
    def __str__(self):
        return f"{self.get_process_type_display()}: {self.get_status_display()}"
    
    @classmethod
    def get_status(cls, process_type, student=None, enrollment=None, semester=None, course_offering=None):
        """Get or create a status record for the given parameters"""
        obj, created = cls.objects.get_or_create(
            process_type=process_type,
            student_id=student.id if student else None,
            enrollment_id=enrollment.id if enrollment else None,
            semester_id=semester.id if semester else None,
            course_offering_id=course_offering.id if course_offering else None,
            defaults={'status': cls.STATUS_NOT_STARTED}
        )
        return obj
    
    def update_status(self, status, message=None, details=None, error_message=None, triggered_by=None):
        """Update the status with optional message and details"""
        self.status = status
        if message:
            self.message = message
        if details:
            self.details.update(details)
        if error_message:
            self.error_message = error_message
        if triggered_by:
            self.triggered_by = triggered_by
        self.save(update_fields=['status', 'message', 'details', 'error_message', 'triggered_by', 'updated_at'])
    
    @classmethod
    def get_result_statuses(cls):
        """Get all possible result statuses"""
        return [
            cls.STATUS_NOT_STARTED,
            cls.STATUS_DRAFT,
            cls.STATUS_INCOMPLETE,
            cls.STATUS_READY,
            cls.STATUS_PROCESSING,
            cls.STATUS_COMPLETED,
            cls.STATUS_PUBLISHED,
            cls.STATUS_FAILED
        ]
    
    @classmethod
    def get_warning_statuses(cls):
        """Get all possible warning statuses"""
        return [
            cls.STATUS_NOT_STARTED,
            cls.STATUS_INCOMPLETE,
            cls.STATUS_READY,
            cls.STATUS_PROCESSING,
            cls.STATUS_COMPLETED,
            cls.STATUS_FAILED
        ]
    
    @classmethod
    def get_attendance_statuses(cls):
        """Get all possible attendance statuses"""
        return [
            cls.STATUS_NOT_STARTED,
            cls.STATUS_PARTIAL,
            cls.STATUS_COMPLETED,
            cls.STATUS_LOCKED,
            cls.STATUS_FAILED
        ]
    
    @classmethod
    def is_complete(cls, status):
        """Check if a status represents completion"""
        return status in [cls.STATUS_COMPLETED, cls.STATUS_PUBLISHED]
    
    @classmethod
    def is_failed(cls, status):
        """Check if a status represents failure"""
        return status == cls.STATUS_FAILED
    
    @classmethod
    def is_actionable(cls, status):
        """Check if action is needed for this status"""
        return status in [cls.STATUS_INCOMPLETE, cls.STATUS_FAILED, cls.STATUS_PARTIAL]


class SystemCalculationLog(models.Model):
    """
    Comprehensive audit log for all academic calculation operations.
    
    Tracks: result recalculation, GPA calculation, warning generation,
    attendance sync, and other automated academic pipeline operations.
    """
    
    # Action types for categorization
    ACTION_ATTENDANCE_RECALC = 'attendance_recalc'
    ACTION_RESULT_RECALC = 'result_recalc'
    ACTION_GPA_RECALC = 'gpa_recalc'
    ACTION_CGPA_RECALC = 'cgpa_recalc'
    ACTION_WARNING_RECALC = 'warning_recalc'
    ACTION_FINAL_RESULT_CALC = 'final_result_calc'
    ACTION_MARK_SYNC = 'mark_sync'
    
    ACTION_CHOICES = [
        (ACTION_ATTENDANCE_RECALC, 'Attendance Recalculation'),
        (ACTION_RESULT_RECALC, 'Result Recalculation'),
        (ACTION_GPA_RECALC, 'GPA Calculation'),
        (ACTION_CGPA_RECALC, 'CGPA Calculation'),
        (ACTION_WARNING_RECALC, 'Warning Calculation'),
        (ACTION_FINAL_RESULT_CALC, 'Final Result Calculation'),
        (ACTION_MARK_SYNC, 'Marks Synchronization'),
    ]
    
    # Status choices
    STATUS_SUCCESS = 'success'
    STATUS_PARTIAL = 'partial'
    STATUS_FAILED = 'failed'
    STATUS_SKIPPED = 'skipped'
    
    STATUS_CHOICES = [
        (STATUS_SUCCESS, 'Success'),
        (STATUS_PARTIAL, 'Partial Success'),
        (STATUS_FAILED, 'Failed'),
        (STATUS_SKIPPED, 'Skipped'),
    ]
    
    # Related entities (nullable for batch operations)
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='calculation_logs',
        help_text='Student associated with this calculation'
    )
    enrollment = models.ForeignKey(
        'enrollments.Enrollment',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='calculation_logs',
        help_text='Enrollment record for this calculation'
    )
    semester = models.ForeignKey(
        'semesters.Semester',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='calculation_logs',
        help_text='Semester context for this calculation'
    )
    course_offering = models.ForeignKey(
        'courses.CourseOffering',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='calculation_logs',
        help_text='Course offering context'
    )
    
    # Action details
    action_type = models.CharField(
        max_length=30,
        choices=ACTION_CHOICES,
        db_index=True,
        help_text='Type of calculation performed'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_SUCCESS,
        db_index=True,
        help_text='Result status of the calculation'
    )
    
    # Message and details
    message = models.TextField(
        blank=True,
        help_text='Human-readable summary of the operation'
    )
    details = models.JSONField(
        default=dict,
        blank=True,
        help_text='Structured data about inputs, outputs, and intermediate values'
    )
    error_message = models.TextField(
        blank=True,
        help_text='Error details if status is failed'
    )
    
    # Audit trail
    triggered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='triggered_calculations',
        help_text='User who triggered this calculation (null for system)'
    )
    triggered_by_name = models.CharField(
        max_length=100,
        blank=True,
        help_text='Cached name of triggering user for historical reference'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    duration_ms = models.IntegerField(
        null=True,
        blank=True,
        help_text='Duration of calculation in milliseconds'
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student', 'action_type', '-created_at']),
            models.Index(fields=['enrollment', 'action_type', '-created_at']),
            models.Index(fields=['action_type', 'status', '-created_at']),
            models.Index(fields=['semester', 'action_type', '-created_at']),
        ]
    
    def __str__(self):
        entity = self.student or self.enrollment or "Batch"
        return f"{self.action_type} - {entity} - {self.status} at {self.created_at}"
    
    def save(self, *args, **kwargs):
        # Cache triggered_by name
        if self.triggered_by and not self.triggered_by_name:
            self.triggered_by_name = self.triggered_by.get_full_name() or self.triggered_by.username
        super().save(*args, **kwargs)


class CalculationLogService:
    """
    Service for creating and managing calculation logs.
    
    Provides a clean API for logging all calculation operations
    throughout the academic pipeline.
    """
    
    @staticmethod
    def log_success(
        action_type: str,
        message: str,
        student=None,
        enrollment=None,
        semester=None,
        course_offering=None,
        details: dict = None,
        triggered_by=None,
        duration_ms: int = None
    ) -> SystemCalculationLog:
        """Create a success log entry."""
        return SystemCalculationLog.objects.create(
            action_type=action_type,
            status=SystemCalculationLog.STATUS_SUCCESS,
            message=message,
            student=student,
            enrollment=enrollment,
            semester=semester,
            course_offering=course_offering,
            details=details or {},
            triggered_by=triggered_by,
            duration_ms=duration_ms
        )
    
    @staticmethod
    def log_failure(
        action_type: str,
        message: str,
        error: Exception = None,
        student=None,
        enrollment=None,
        semester=None,
        course_offering=None,
        details: dict = None,
        triggered_by=None,
        duration_ms: int = None
    ) -> SystemCalculationLog:
        """Create a failure log entry with error details."""
        error_msg = str(error) if error else None
        
        return SystemCalculationLog.objects.create(
            action_type=action_type,
            status=SystemCalculationLog.STATUS_FAILED,
            message=message,
            error_message=error_msg,
            student=student,
            enrollment=enrollment,
            semester=semester,
            course_offering=course_offering,
            details=details or {},
            triggered_by=triggered_by,
            duration_ms=duration_ms
        )
    
    @staticmethod
    def log_partial(
        action_type: str,
        message: str,
        student=None,
        enrollment=None,
        semester=None,
        course_offering=None,
        details: dict = None,
        triggered_by=None,
        duration_ms: int = None
    ) -> SystemCalculationLog:
        """Create a partial success log entry."""
        return SystemCalculationLog.objects.create(
            action_type=action_type,
            status=SystemCalculationLog.STATUS_PARTIAL,
            message=message,
            student=student,
            enrollment=enrollment,
            semester=semester,
            course_offering=course_offering,
            details=details or {},
            triggered_by=triggered_by,
            duration_ms=duration_ms
        )
    
    @staticmethod
    def log_skipped(
        action_type: str,
        message: str,
        student=None,
        enrollment=None,
        semester=None,
        course_offering=None,
        details: dict = None,
        triggered_by=None
    ) -> SystemCalculationLog:
        """Create a skipped log entry (e.g., insufficient data)."""
        return SystemCalculationLog.objects.create(
            action_type=action_type,
            status=SystemCalculationLog.STATUS_SKIPPED,
            message=message,
            student=student,
            enrollment=enrollment,
            semester=semester,
            course_offering=course_offering,
            details=details or {},
            triggered_by=triggered_by
        )

