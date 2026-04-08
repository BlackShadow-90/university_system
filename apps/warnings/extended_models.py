"""
Extended warning system models for intervention tracking and workflow
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from apps.students.models import Student
from apps.semesters.models import Semester
from apps.teachers.models import Teacher


class WarningIntervention(models.Model):
    """Track interventions/actions taken for student warnings"""
    
    INTERVENTION_TYPE_CHOICES = [
        ('meeting_scheduled', _('Meeting Scheduled')),
        ('meeting_completed', _('Meeting Completed')),
        ('tutoring_assigned', _('Tutoring Assigned')),
        ('study_plan_created', _('Study Plan Created')),
        ('advisor_consultation', _('Advisor Consultation')),
        ('parent_notified', _('Parent/Guardian Notified')),
        ('attendance_contract', _('Attendance Contract Signed')),
        ('academic_probation', _('Academic Probation Assigned')),
        ('course_withdrawal', _('Course Withdrawal Recommended')),
        ('counseling_referral', _('Counseling Referral')),
        ('other', _('Other Action')),
    ]
    
    STATUS_CHOICES = [
        ('planned', _('Planned')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
        ('follow_up_needed', _('Follow-up Needed')),
    ]
    
    warning = models.ForeignKey(
        'warnings.EarlyWarningResult',
        on_delete=models.CASCADE,
        related_name='interventions',
        verbose_name=_('Related Warning')
    )
    
    intervention_type = models.CharField(
        _('Intervention Type'),
        max_length=30,
        choices=INTERVENTION_TYPE_CHOICES
    )
    
    description = models.TextField(
        _('Description'),
        help_text=_('Detailed description of the intervention')
    )
    
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='planned'
    )
    
    initiated_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='initiated_interventions',
        verbose_name=_('Initiated By')
    )
    
    assigned_to = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_interventions',
        verbose_name=_('Assigned To')
    )
    
    scheduled_date = models.DateTimeField(
        _('Scheduled Date'),
        null=True,
        blank=True
    )
    
    completed_date = models.DateTimeField(
        _('Completed Date'),
        null=True,
        blank=True
    )
    
    outcome_notes = models.TextField(
        _('Outcome Notes'),
        blank=True,
        help_text=_('Results and observations after intervention')
    )
    
    follow_up_date = models.DateTimeField(
        _('Follow-up Date'),
        null=True,
        blank=True
    )
    
    is_effective = models.BooleanField(
        _('Was Effective'),
        null=True,
        blank=True,
        help_text=_('Whether the intervention achieved desired results')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'warning_interventions'
        verbose_name = _('Warning Intervention')
        verbose_name_plural = _('Warning Interventions')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_intervention_type_display()} - {self.warning.student.student_no}"
    
    def mark_completed(self, outcome_notes='', is_effective=None):
        """Mark intervention as completed"""
        self.status = 'completed'
        self.completed_date = timezone.now()
        if outcome_notes:
            self.outcome_notes = outcome_notes
        if is_effective is not None:
            self.is_effective = is_effective
        self.save(update_fields=['status', 'completed_date', 'outcome_notes', 'is_effective'])


class WarningHistory(models.Model):
    """Track history of warning changes and escalations"""
    
    CHANGE_TYPE_CHOICES = [
        ('created', _('Warning Created')),
        ('level_changed', _('Warning Level Changed')),
        ('escalated', _('Warning Escalated')),
        ('de_escalated', _('Warning De-escalated')),
        ('acknowledged', _('Warning Acknowledged')),
        ('resolved', _('Warning Resolved')),
        ('reopened', _('Warning Reopened')),
        ('intervention_added', _('Intervention Added')),
        ('intervention_completed', _('Intervention Completed')),
        ('notes_added', _('Notes Added')),
        ('auto_calculated', _('Auto-calculated')),
    ]
    
    warning = models.ForeignKey(
        'warnings.EarlyWarningResult',
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name=_('Related Warning')
    )
    
    change_type = models.CharField(
        _('Change Type'),
        max_length=30,
        choices=CHANGE_TYPE_CHOICES
    )
    
    previous_level = models.CharField(
        _('Previous Warning Level'),
        max_length=20,
        blank=True
    )
    
    new_level = models.CharField(
        _('New Warning Level'),
        max_length=20,
        blank=True
    )
    
    previous_risk_score = models.DecimalField(
        _('Previous Risk Score'),
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    new_risk_score = models.DecimalField(
        _('New Risk Score'),
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    notes = models.TextField(
        _('Notes'),
        blank=True
    )
    
    triggered_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='warning_history_entries',
        verbose_name=_('Triggered By')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'warning_history'
        verbose_name = _('Warning History')
        verbose_name_plural = _('Warning History')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_change_type_display()} - {self.warning.student.student_no} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class WarningEvidence(models.Model):
    """Store evidence for why student was flagged"""
    
    EVIDENCE_TYPE_CHOICES = [
        ('attendance_record', _('Attendance Record')),
        ('grade_record', _('Grade Record')),
        ('assignment_missing', _('Missing Assignment')),
        ('teacher_observation', _('Teacher Observation')),
        ('behavioral_report', _('Behavioral Report')),
        ('screenshot', _('Screenshot')),
        ('document', _('Document')),
        ('other', _('Other')),
    ]
    
    warning = models.ForeignKey(
        'warnings.EarlyWarningResult',
        on_delete=models.CASCADE,
        related_name='evidence',
        verbose_name=_('Related Warning')
    )
    
    evidence_type = models.CharField(
        _('Evidence Type'),
        max_length=30,
        choices=EVIDENCE_TYPE_CHOICES
    )
    
    title = models.CharField(
        _('Title'),
        max_length=200
    )
    
    description = models.TextField(
        _('Description'),
        blank=True
    )
    
    file_attachment = models.FileField(
        _('File Attachment'),
        upload_to='warning_evidence/%Y/%m/',
        null=True,
        blank=True
    )
    
    data_snapshot = models.JSONField(
        _('Data Snapshot'),
        default=dict,
        blank=True,
        help_text=_('JSON snapshot of relevant data at time of warning')
    )
    
    captured_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='captured_evidence',
        verbose_name=_('Captured By')
    )
    
    captured_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'warning_evidence'
        verbose_name = _('Warning Evidence')
        verbose_name_plural = _('Warning Evidence')
        ordering = ['-captured_at']
    
    def __str__(self):
        return f"{self.title} - {self.warning.student.student_no}"


class WarningEscalationRule(models.Model):
    """Rules for automatic warning escalation"""
    
    name = models.CharField(
        _('Rule Name'),
        max_length=100
    )
    
    description = models.TextField(
        _('Description'),
        blank=True
    )
    
    from_level = models.CharField(
        _('From Level'),
        max_length=20,
        choices=[
            ('green', _('Green - Stable')),
            ('yellow', _('Yellow - Mild Warning')),
            ('orange', _('Orange - Serious Warning')),
            ('red', _('Red - Critical Warning')),
        ]
    )
    
    to_level = models.CharField(
        _('To Level'),
        max_length=20,
        choices=[
            ('green', _('Green - Stable')),
            ('yellow', _('Yellow - Mild Warning')),
            ('orange', _('Orange - Serious Warning')),
            ('red', _('Red - Critical Warning')),
        ]
    )
    
    days_without_improvement = models.PositiveIntegerField(
        _('Days Without Improvement'),
        default=7,
        help_text=_('Number of days to wait before escalating if no improvement')
    )
    
    requires_intervention_attempt = models.BooleanField(
        _('Requires Intervention Attempt'),
        default=True,
        help_text=_('Only escalate if at least one intervention was attempted')
    )
    
    auto_notify_parents = models.BooleanField(
        _('Auto-notify Parents'),
        default=False
    )
    
    auto_notify_advisor = models.BooleanField(
        _('Auto-notify Advisor'),
        default=True
    )
    
    is_active = models.BooleanField(
        _('Is Active'),
        default=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'warning_escalation_rules'
        verbose_name = _('Warning Escalation Rule')
        verbose_name_plural = _('Warning Escalation Rules')
    
    def __str__(self):
        return f"{self.name}: {self.from_level} → {self.to_level}"


class WarningResolution(models.Model):
    """Track warning resolutions and outcomes"""
    
    RESOLUTION_TYPE_CHOICES = [
        ('improved_performance', _('Improved Performance')),
        ('attendance_recovered', _('Attendance Recovered')),
        ('completed_intervention', _('Completed Intervention Program')),
        ('withdrawal_approved', _('Course Withdrawal Approved')),
        ('semester_completed', _('Semester Completed')),
        ('transferred', _('Student Transferred')),
        ('other', _('Other')),
    ]
    
    warning = models.OneToOneField(
        'warnings.EarlyWarningResult',
        on_delete=models.CASCADE,
        related_name='resolution',
        verbose_name=_('Related Warning')
    )
    
    resolution_type = models.CharField(
        _('Resolution Type'),
        max_length=30,
        choices=RESOLUTION_TYPE_CHOICES
    )
    
    resolution_notes = models.TextField(
        _('Resolution Notes'),
        help_text=_('How the warning was resolved')
    )
    
    resolved_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='resolved_warnings',
        verbose_name=_('Resolved By')
    )
    
    final_risk_score = models.DecimalField(
        _('Final Risk Score'),
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    improvement_metrics = models.JSONField(
        _('Improvement Metrics'),
        default=dict,
        blank=True,
        help_text=_('Quantifiable improvements (attendance %, GPA change, etc.)')
    )
    
    requires_monitoring = models.BooleanField(
        _('Requires Continued Monitoring'),
        default=False
    )
    
    monitoring_end_date = models.DateField(
        _('Monitoring End Date'),
        null=True,
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'warning_resolutions'
        verbose_name = _('Warning Resolution')
        verbose_name_plural = _('Warning Resolutions')
    
    def __str__(self):
        return f"Resolved: {self.warning.student.student_no} - {self.get_resolution_type_display()}"
