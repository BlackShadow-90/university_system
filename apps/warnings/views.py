"""
Views for complete warning system management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.utils import timezone

from apps.core.services import admin_required, teacher_required, student_required
from apps.warnings.models import EarlyWarningResult, EarlyWarningRule
from apps.warnings.extended_models import (
    WarningIntervention, WarningHistory, WarningEvidence,
    ParentGuardianNotification, WarningResolution
)
from apps.warnings.services import WarningSystemService
from apps.students.models import Student


@method_decorator(login_required, name='dispatch')
@method_decorator(teacher_required, name='dispatch')
class WarningDetailView(DetailView):
    """Detailed view of a warning with interventions and timeline"""
    model = EarlyWarningResult
    template_name = 'warnings/warning_detail.html'
    context_object_name = 'warning'
    pk_url_kwarg = 'pk'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        warning = self.get_object()
        
        # Get timeline
        context['timeline'] = WarningSystemService.get_warning_timeline(warning)
        
        # Get interventions
        context['interventions'] = warning.interventions.select_related(
            'initiated_by', 'assigned_to'
        ).order_by('-created_at')
        
        # Get evidence
        context['evidence'] = warning.evidence.select_related('captured_by').all()
        
        # Get parent notifications
        context['parent_notifications'] = warning.parent_notifications.all()
        
        # Check if resolved
        context['resolution'] = getattr(warning, 'resolution', None)
        
        # Get available intervention types for forms
        context['intervention_types'] = WarningIntervention.INTERVENTION_TYPE_CHOICES
        
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(teacher_required, name='dispatch')
class CreateInterventionView(CreateView):
    """Create a new intervention for a warning"""
    model = WarningIntervention
    fields = ['intervention_type', 'description', 'assigned_to', 'scheduled_date']
    template_name = 'warnings/intervention_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.warning = get_object_or_404(EarlyWarningResult, pk=kwargs['warning_pk'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['warning'] = self.warning
        return context
    
    def form_valid(self, form):
        intervention = form.save(commit=False)
        intervention.warning = self.warning
        intervention.initiated_by = self.request.user
        intervention.save()
        
        messages.success(self.request, _('Intervention created successfully.'))
        return redirect('warnings:warning_detail', pk=self.warning.pk)


@method_decorator(login_required, name='dispatch')
@method_decorator(teacher_required, name='dispatch')
class CompleteInterventionView(View):
    """Complete an intervention and record outcome"""
    
    def post(self, request, intervention_pk):
        intervention = get_object_or_404(WarningIntervention, pk=intervention_pk)
        
        outcome_notes = request.POST.get('outcome_notes', '')
        is_effective = request.POST.get('is_effective') == 'true'
        
        WarningSystemService.complete_intervention(
            intervention=intervention,
            outcome_notes=outcome_notes,
            is_effective=is_effective,
            completed_by=request.user
        )
        
        messages.success(request, _('Intervention marked as completed.'))
        return redirect('warnings:warning_detail', pk=intervention.warning.pk)


@method_decorator(login_required, name='dispatch')
@method_decorator(teacher_required, name='dispatch')
class AddEvidenceView(View):
    """Add evidence to a warning"""
    
    def post(self, request, warning_pk):
        warning = get_object_or_404(EarlyWarningResult, pk=warning_pk)
        
        evidence_type = request.POST.get('evidence_type')
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        file_attachment = request.FILES.get('file_attachment')
        
        WarningSystemService.add_evidence(
            warning=warning,
            evidence_type=evidence_type,
            title=title,
            description=description,
            captured_by=request.user,
            file_attachment=file_attachment
        )
        
        messages.success(request, _('Evidence added successfully.'))
        return redirect('warnings:warning_detail', pk=warning.pk)


@method_decorator(login_required, name='dispatch')
@method_decorator(teacher_required, name='dispatch')
class EscalateWarningView(View):
    """Escalate or de-escalate a warning"""
    
    def post(self, request, warning_pk):
        warning = get_object_or_404(EarlyWarningResult, pk=warning_pk)
        
        new_level = request.POST.get('new_level')
        reason = request.POST.get('reason', '')
        
        if new_level not in ['green', 'yellow', 'orange', 'red']:
            messages.error(request, _('Invalid warning level.'))
            return redirect('warnings:warning_detail', pk=warning.pk)
        
        WarningSystemService.escalate_warning(
            warning=warning,
            new_level=new_level,
            reason=reason,
            triggered_by=request.user
        )
        
        level_name = dict(EarlyWarningResult.WARNING_LEVEL_CHOICES).get(new_level)
        messages.success(
            request, 
            _('Warning level changed to %(level)s.') % {'level': level_name}
        )
        return redirect('warnings:warning_detail', pk=warning.pk)


@method_decorator(login_required, name='dispatch')
@method_decorator(teacher_required, name='dispatch')
class ResolveWarningView(View):
    """Resolve a warning"""
    
    def post(self, request, warning_pk):
        warning = get_object_or_404(EarlyWarningResult, pk=warning_pk)
        
        resolution_type = request.POST.get('resolution_type')
        resolution_notes = request.POST.get('resolution_notes', '')
        
        # Check if already resolved
        if hasattr(warning, 'resolution'):
            messages.error(request, _('This warning has already been resolved.'))
            return redirect('warnings:warning_detail', pk=warning.pk)
        
        WarningSystemService.resolve_warning(
            warning=warning,
            resolution_type=resolution_type,
            resolution_notes=resolution_notes,
            resolved_by=request.user
        )
        
        messages.success(request, _('Warning has been resolved.'))
        return redirect('warnings:warning_detail', pk=warning.pk)


@method_decorator(login_required, name='dispatch')
@method_decorator(teacher_required, name='dispatch')
class NotifyParentsView(View):
    """Send notification to parents/guardians"""
    
    def post(self, request, warning_pk):
        warning = get_object_or_404(EarlyWarningResult, pk=warning_pk)
        
        notification_type = request.POST.get('notification_type', 'new_warning')
        
        notification = WarningSystemService.notify_parents(warning, notification_type)
        
        if notification:
            messages.success(request, _('Parent/Guardian notification sent.'))
        else:
            messages.warning(
                request, 
                _('Could not send notification - no parent contact information available.')
            )
        
        return redirect('warnings:warning_detail', pk=warning.pk)


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class RunAutoEscalationView(View):
    """Run automatic escalation check (admin only)"""
    
    def post(self, request):
        count = WarningSystemService.check_for_auto_escalation()
        
        messages.success(
            request, 
            _('Automatic escalation check completed. %(count)d warning(s) escalated.') 
            % {'count': count}
        )
        return redirect('admin_portal:admin_warnings')


@method_decorator(login_required, name='dispatch')
@method_decorator(teacher_required, name='dispatch')
class WarningStatisticsView(View):
    """View warning statistics"""
    
    def get(self, request):
        semester_id = request.GET.get('semester')
        program_id = request.GET.get('program')
        
        semester = None
        program = None
        
        if semester_id:
            from apps.semesters.models import Semester
            semester = get_object_or_404(Semester, pk=semester_id)
        
        if program_id:
            from apps.programs.models import Program
            program = get_object_or_404(Program, pk=program_id)
        
        stats = WarningSystemService.calculate_warning_statistics(semester, program)
        
        context = {
            'statistics': stats,
            'semester': semester,
            'program': program,
        }
        
        return render(request, 'warnings/statistics.html', context)


@method_decorator(login_required, name='dispatch')
@method_decorator(teacher_required, name='dispatch')
class AtRiskStudentsListView(ListView):
    """List at-risk students with filtering"""
    model = EarlyWarningResult
    template_name = 'warnings/at_risk_list.html'
    context_object_name = 'warnings'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = EarlyWarningResult.objects.exclude(
            warning_level='green'
        ).select_related(
            'student', 'student__program', 'semester'
        ).prefetch_related('interventions')
        
        # Filter by level
        level = self.request.GET.get('level')
        if level:
            queryset = queryset.filter(warning_level=level)
        
        # Filter by acknowledgment status
        acknowledged = self.request.GET.get('acknowledged')
        if acknowledged == 'yes':
            queryset = queryset.filter(is_acknowledged=True)
        elif acknowledged == 'no':
            queryset = queryset.filter(is_acknowledged=False)
        
        # Filter by intervention status
        has_intervention = self.request.GET.get('has_intervention')
        if has_intervention == 'yes':
            queryset = queryset.filter(interventions__isnull=False).distinct()
        elif has_intervention == 'no':
            queryset = queryset.filter(interventions__isnull=True)
        
        return queryset.order_by('-risk_score')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['warning_levels'] = EarlyWarningResult.WARNING_LEVEL_CHOICES
        context['filters'] = {
            'level': self.request.GET.get('level', ''),
            'acknowledged': self.request.GET.get('acknowledged', ''),
            'has_intervention': self.request.GET.get('has_intervention', ''),
        }
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(student_required, name='dispatch')
class StudentWarningCenterView(ListView):
    """Student view of their own warnings"""
    model = EarlyWarningResult
    template_name = 'student_portal/warnings/center.html'
    context_object_name = 'warnings'
    
    def get_queryset(self):
        return EarlyWarningResult.objects.filter(
            student=self.request.user.student_profile
        ).select_related('semester').prefetch_related('interventions', 'resolution')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get statistics for the student
        student_warnings = self.get_queryset()
        context['active_warnings'] = student_warnings.exclude(warning_level='green').count()
        context['acknowledged_warnings'] = student_warnings.filter(is_acknowledged=True).count()
        context['resolved_warnings'] = WarningResolution.objects.filter(
            warning__in=student_warnings
        ).count()
        
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(student_required, name='dispatch')
class AcknowledgeWarningView(View):
    """Student acknowledges a warning"""
    
    def post(self, request, pk):
        warning = get_object_or_404(
            EarlyWarningResult, 
            pk=pk, 
            student=request.user.student_profile
        )
        
        if not warning.is_acknowledged:
            warning.is_acknowledged = True
            warning.acknowledged_at = timezone.now()
            warning.save(update_fields=['is_acknowledged', 'acknowledged_at'])
            
            # Log the acknowledgment
            WarningHistory.objects.create(
                warning=warning,
                change_type='acknowledged',
                notes='Warning acknowledged by student',
                triggered_by=request.user
            )
            
            messages.success(request, _('Warning acknowledged. Please review the recommendations.'))
        
        return redirect('student_portal:student_warnings')
