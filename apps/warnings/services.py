"""
Complete warning system service with escalation, interventions, and workflow
"""
from django.utils import timezone
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from apps.warnings.models import EarlyWarningResult, EarlyWarningRule
from apps.warnings.extended_models import (
    WarningIntervention, WarningHistory, WarningEvidence,
    WarningEscalationRule, WarningResolution
)
from apps.notifications.services import NotificationService


class WarningSystemService:
    """Complete service for warning system management"""
    
    @staticmethod
    def create_intervention(warning, intervention_type, description, initiated_by, 
                           assigned_to=None, scheduled_date=None):
        """Create a new intervention for a warning"""
        intervention = WarningIntervention.objects.create(
            warning=warning,
            intervention_type=intervention_type,
            description=description,
            initiated_by=initiated_by,
            assigned_to=assigned_to,
            scheduled_date=scheduled_date,
            status='planned'
        )
        
        # Log the intervention creation
        WarningHistory.objects.create(
            warning=warning,
            change_type='intervention_added',
            notes=f"Intervention created: {intervention.get_intervention_type_display()}",
            triggered_by=initiated_by
        )
        
        # Notify assigned teacher if applicable
        if assigned_to and assigned_to.user:
            NotificationService.send_notification(
                recipient=assigned_to.user,
                title_en="New Intervention Assigned",
                title_zh="新干预任务已分配",
                content_en=f"You have been assigned to intervene with student {warning.student.student_no} "
                          f"for {intervention.get_intervention_type_display()}",
                content_zh=f"您被分配干预学生 {warning.student.student_no}，"
                          f"干预类型：{intervention.get_intervention_type_display()}",
                notification_type='warning',
                related_object=intervention
            )
        
        return intervention
    
    @staticmethod
    def complete_intervention(intervention, outcome_notes, is_effective, completed_by):
        """Mark an intervention as completed"""
        intervention.mark_completed(outcome_notes, is_effective)
        
        # Log the completion
        WarningHistory.objects.create(
            warning=intervention.warning,
            change_type='intervention_completed',
            notes=f"Intervention completed: {intervention.get_intervention_type_display()}. "
                  f"Outcome: {outcome_notes[:100]}",
            triggered_by=completed_by
        )
        
        # If effective, check if warning can be de-escalated
        if is_effective:
            WarningSystemService.check_for_de_escalation(intervention.warning)
        
        return intervention
    
    @staticmethod
    def add_evidence(warning, evidence_type, title, description, captured_by, 
                     file_attachment=None, data_snapshot=None):
        """Add evidence to a warning"""
        evidence = WarningEvidence.objects.create(
            warning=warning,
            evidence_type=evidence_type,
            title=title,
            description=description,
            captured_by=captured_by,
            file_attachment=file_attachment,
            data_snapshot=data_snapshot or {}
        )
        return evidence
    
    @staticmethod
    def escalate_warning(warning, new_level, notes, triggered_by):
        """Escalate a warning to a new level"""
        old_level = warning.warning_level
        
        if old_level == new_level:
            return warning
        
        with transaction.atomic():
            # Update warning level
            warning.warning_level = new_level
            warning.save(update_fields=['warning_level', 'updated_at'])
            
            # Create history record
            WarningHistory.objects.create(
                warning=warning,
                change_type='escalation',
                old_level=old_level,
                new_level=new_level,
                notes=notes,
                triggered_by=triggered_by
            )
            
            # Notify student
            if warning.student.user:
                level_names = {
                    'green': ('Stable', '稳定'),
                    'yellow': ('Mild Warning', '轻度警告'),
                    'orange': ('Serious Warning', '严重警告'),
                    'red': ('Critical Warning', '危急警告')
                }
                old_name_en, old_name_zh = level_names.get(old_level, (old_level, old_level))
                new_name_en, new_name_zh = level_names.get(new_level, (new_level, new_level))
                
                NotificationService.send_notification(
                    recipient=warning.student.user,
                    title_en=f"Warning Level Changed: {new_name_en}",
                    title_zh=f"警告级别变更：{new_name_zh}",
                    content_en=f"Your academic warning level has changed from {old_name_en} to {new_name_en}. "
                              f"Please check the warning center immediately.",
                    content_zh=f"您的学术警告级别已从 {old_name_zh} 变更为 {new_name_zh}。 "
                              f"请立即查看警告中心。",
                    notification_type='warning',
                    priority='urgent',
                    related_object=warning
                )
        
        return warning
    
    @staticmethod
    def check_for_auto_escalation():
        """Check all warnings for automatic escalation based on rules"""
        escalated_count = 0
        
        active_rules = WarningEscalationRule.objects.filter(is_active=True)
        
        for rule in active_rules:
            # Find warnings at the 'from' level that haven't improved
            warnings = EarlyWarningResult.objects.filter(
                warning_level=rule.from_level,
                is_acknowledged=False
            )
            
            for warning in warnings:
                days_since_created = (timezone.now() - warning.generated_at).days
                
                if days_since_created >= rule.days_without_improvement:
                    # Check if intervention was attempted
                    has_intervention = warning.interventions.filter(
                        status__in=['completed', 'in_progress']
                    ).exists()
                    
                    if rule.requires_intervention_attempt and not has_intervention:
                        continue
                    
                    # Check if risk score hasn't improved
                    recent_history = warning.history.filter(
                        change_type='auto_calculated'
                    ).order_by('-created_at').first()
                    
                    if recent_history and recent_history.new_risk_score >= warning.risk_score:
                        # No improvement - escalate
                        WarningSystemService.escalate_warning(
                            warning,
                            rule.to_level,
                            f"Auto-escalated after {days_since_created} days without improvement",
                            None  # System-triggered
                        )
                        escalated_count += 1
        
        return escalated_count
    
    @staticmethod
    def check_for_de_escalation(warning):
        """Check if warning can be de-escalated based on improvements"""
        # Check if recent interventions were effective
        recent_interventions = warning.interventions.filter(
            created_at__gte=timezone.now() - timezone.timedelta(days=14)
        )
        
        if not recent_interventions.exists():
            return warning
        
        # Check if most interventions were effective
        effective_count = recent_interventions.filter(is_effective=True).count()
        total_count = recent_interventions.count()
        
        if total_count > 0 and (effective_count / total_count) >= 0.7:
            # 70% or more interventions were effective - de-escalate
            current_level = warning.warning_level
            
            de_escalation_map = {
                'red': 'orange',
                'orange': 'yellow',
                'yellow': 'green'
            }
            
            new_level = de_escalation_map.get(current_level)
            if new_level:
                WarningSystemService.escalate_warning(
                    warning,
                    new_level,
                    "De-escalated due to improvement in student performance",
                    None
                )
        
        return warning
    
    @staticmethod
    def resolve_warning(warning, resolution_type, resolution_notes, resolved_by, 
                       improvement_metrics=None):
        """Resolve a warning"""
        with transaction.atomic():
            # Create resolution record
            resolution = WarningResolution.objects.create(
                warning=warning,
                resolution_type=resolution_type,
                resolution_notes=resolution_notes,
                resolved_by=resolved_by,
                final_risk_score=warning.risk_score,
                improvement_metrics=improvement_metrics or {}
            )
            
            # Log the resolution
            WarningHistory.objects.create(
                warning=warning,
                change_type='resolved',
                new_level='green',
                notes=f"Warning resolved: {resolution.get_resolution_type_display()}. "
                      f"Notes: {resolution_notes[:100]}",
                triggered_by=resolved_by
            )
            
            # Notify student
            if warning.student.user:
                NotificationService.send_notification(
                    recipient=warning.student.user,
                    title_en="Academic Warning Resolved",
                    title_zh="学术警告已解除",
                    content_en="Your academic warning has been resolved. "
                              "Keep up the good work!",
                    content_zh="您的学术警告已解除。请继续保持良好的学习状态！",
                    notification_type='academic',
                    related_object=warning
                )
            
            return resolution
    
    @staticmethod
    def get_warning_timeline(warning):
        """Get complete timeline of warning history"""
        timeline = []
        
        # Warning creation
        timeline.append({
            'date': warning.generated_at,
            'type': 'created',
            'title': _('Warning Created'),
            'description': f"Initial risk score: {warning.risk_score}",
            'level': warning.warning_level
        })
        
        # History entries
        for history in warning.history.all():
            timeline.append({
                'date': history.created_at,
                'type': history.change_type,
                'title': history.get_change_type_display(),
                'description': history.notes,
                'level': history.new_level or warning.warning_level,
                'user': history.triggered_by.get_full_name() if history.triggered_by else _('System')
            })
        
        # Interventions
        for intervention in warning.interventions.all():
            timeline.append({
                'date': intervention.created_at,
                'type': 'intervention',
                'title': f"Intervention: {intervention.get_intervention_type_display()}",
                'description': intervention.description[:100],
                'status': intervention.status,
                'user': intervention.initiated_by.get_full_name() if intervention.initiated_by else None
            })
            
            if intervention.completed_date:
                timeline.append({
                    'date': intervention.completed_date,
                    'type': 'intervention_completed',
                    'title': f"Intervention Completed: {intervention.get_intervention_type_display()}",
                    'description': intervention.outcome_notes[:100] if intervention.outcome_notes else '',
                    'effective': intervention.is_effective
                })
        
        # Sort by date
        timeline.sort(key=lambda x: x['date'])
        
        return timeline
    
    @staticmethod
    def calculate_warning_statistics(semester=None, program=None):
        """Calculate warning statistics for dashboard"""
        warnings = EarlyWarningResult.objects.all()
        
        if semester:
            warnings = warnings.filter(semester=semester)
        
        if program:
            warnings = warnings.filter(student__program=program)
        
        stats = {
            'total_warnings': warnings.count(),
            'by_level': {
                'green': warnings.filter(warning_level='green').count(),
                'yellow': warnings.filter(warning_level='yellow').count(),
                'orange': warnings.filter(warning_level='orange').count(),
                'red': warnings.filter(warning_level='red').count(),
            },
            'acknowledged': warnings.filter(is_acknowledged=True).count(),
            'unacknowledged': warnings.filter(is_acknowledged=False).count(),
            'with_interventions': warnings.filter(interventions__isnull=False).distinct().count(),
            'resolved': WarningResolution.objects.filter(
                warning__in=warnings
            ).count(),
            'avg_risk_score': warnings.filter(risk_score__gt=0).aggregate(
                avg=models.Avg('risk_score')
            )['avg'] or 0
        }
        
        return stats


# Import needed for aggregation
from django.db import models
