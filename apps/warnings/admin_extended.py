"""
Admin configuration for warning system extended models
"""
from django.contrib import admin
from .extended_models import (
    WarningIntervention, WarningHistory, WarningEvidence,
    WarningEscalationRule, WarningResolution
)


@admin.register(WarningIntervention)
class WarningInterventionAdmin(admin.ModelAdmin):
    list_display = ['warning', 'intervention_type', 'status', 'initiated_by', 'created_at']
    list_filter = ['intervention_type', 'status', 'is_effective']
    search_fields = ['warning__student__student_no', 'description']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': ('warning', 'intervention_type', 'description', 'status')
        }),
        ('Assignment', {
            'fields': ('initiated_by', 'assigned_to')
        }),
        ('Scheduling', {
            'fields': ('scheduled_date', 'completed_date')
        }),
        ('Outcome', {
            'fields': ('outcome_notes', 'is_effective', 'follow_up_date')
        }),
    )


@admin.register(WarningHistory)
class WarningHistoryAdmin(admin.ModelAdmin):
    list_display = ['warning', 'change_type', 'previous_level', 'new_level', 'created_at']
    list_filter = ['change_type']
    search_fields = ['warning__student__student_no', 'notes']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']


@admin.register(WarningEvidence)
class WarningEvidenceAdmin(admin.ModelAdmin):
    list_display = ['warning', 'evidence_type', 'title', 'captured_by', 'captured_at']
    list_filter = ['evidence_type']
    search_fields = ['title', 'description', 'warning__student__student_no']
    date_hierarchy = 'captured_at'


@admin.register(WarningEscalationRule)
class WarningEscalationRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'from_level', 'to_level', 'days_without_improvement', 'is_active']
    list_filter = ['is_active', 'from_level', 'to_level']
    search_fields = ['name', 'description']


@admin.register(WarningResolution)
class WarningResolutionAdmin(admin.ModelAdmin):
    list_display = ['warning', 'resolution_type', 'resolved_by', 'created_at']
    list_filter = ['resolution_type']
    search_fields = ['warning__student__student_no', 'resolution_notes']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']
