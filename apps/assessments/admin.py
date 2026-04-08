from django.contrib import admin
from .models import AssessmentComponent, AssessmentScore


@admin.register(AssessmentComponent)
class AssessmentComponentAdmin(admin.ModelAdmin):
    list_display = ['course_offering', 'name', 'assessment_type', 'weight_percentage', 'max_score', 'order']
    list_filter = ['assessment_type', 'course_offering__semester']
    search_fields = ['name', 'course_offering__course__code']
    raw_id_fields = ['course_offering']


@admin.register(AssessmentScore)
class AssessmentScoreAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'assessment_component', 'score', 'percentage', 'status', 'entered_by']
    list_filter = ['status', 'assessment_component__assessment_type']
    search_fields = ['enrollment__student__student_no']
    raw_id_fields = ['enrollment', 'assessment_component', 'entered_by']
