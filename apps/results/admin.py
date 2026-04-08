from django.contrib import admin
from .models import FinalResult, GradeScheme, GradeMapping
from .summary_models import SemesterSummary, CGPARecord


@admin.register(FinalResult)
class FinalResultAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'total_score', 'letter_grade', 'grade_point', 'pass_fail_status', 'is_published']
    list_filter = ['is_published', 'pass_fail_status', 'letter_grade']
    search_fields = ['enrollment__student__student_no']
    raw_id_fields = ['enrollment', 'published_by']


@admin.register(GradeScheme)
class GradeSchemeAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_default', 'description']
    list_filter = ['is_default']


@admin.register(GradeMapping)
class GradeMappingAdmin(admin.ModelAdmin):
    list_display = ['scheme', 'letter_grade', 'grade_point', 'min_percentage', 'max_percentage', 'is_passing']
    list_filter = ['scheme', 'is_passing']
    ordering = ['scheme', '-order']


@admin.register(SemesterSummary)
class SemesterSummaryAdmin(admin.ModelAdmin):
    list_display = ['student', 'semester', 'semester_gpa', 'semester_credits_earned', 'warning_level', 'computed_at']
    list_filter = ['warning_level', 'semester']
    search_fields = ['student__student_no']


@admin.register(CGPARecord)
class CGPARecordAdmin(admin.ModelAdmin):
    list_display = ['student', 'cumulative_gpa', 'cumulative_credits_earned', 'computed_at']
    search_fields = ['student__student_no']
