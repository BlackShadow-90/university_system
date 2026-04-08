from django.contrib import admin
from .models import EarlyWarningRule, EarlyWarningResult
from .extended_models import (
    WarningIntervention, WarningHistory, WarningEvidence,
    WarningEscalationRule, WarningResolution
)


@admin.register(EarlyWarningRule)
class EarlyWarningRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'threshold_value', 'weight', 'severity', 'is_active', 'order']
    list_filter = ['category', 'severity', 'is_active']
    search_fields = ['name', 'code']


@admin.register(EarlyWarningResult)
class EarlyWarningResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'semester', 'risk_score', 'warning_level', 'is_acknowledged', 'generated_at']
    list_filter = ['warning_level', 'is_acknowledged', 'semester']
    search_fields = ['student__student_no']
    raw_id_fields = ['student', 'semester']


@admin.register(WarningIntervention)
class WarningInterventionAdmin(admin.ModelAdmin):
    list_display = ['warning', 'intervention_type', 'status', 'initiated_by', 'created_at']
    list_filter = ['intervention_type', 'status']
    search_fields = ['warning__student__student_no', 'description']
    date_hierarchy = 'created_at'


@admin.register(WarningHistory)
class WarningHistoryAdmin(admin.ModelAdmin):
    list_display = ['warning', 'change_type', 'previous_level', 'new_level', 'created_at']
    list_filter = ['change_type']
    search_fields = ['warning__student__student_no', 'notes']
    date_hierarchy = 'created_at'


@admin.register(WarningEvidence)
class WarningEvidenceAdmin(admin.ModelAdmin):
    list_display = ['warning', 'evidence_type', 'title', 'captured_by', 'captured_at']
    list_filter = ['evidence_type']
    search_fields = ['title', 'warning__student__student_no']


@admin.register(WarningEscalationRule)
class WarningEscalationRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'from_level', 'to_level', 'days_without_improvement', 'is_active']
    list_filter = ['is_active']


@admin.register(WarningResolution)
class WarningResolutionAdmin(admin.ModelAdmin):
    list_display = ['warning', 'resolution_type', 'resolved_by', 'created_at']
    list_filter = ['resolution_type']
