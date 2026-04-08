from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.utils.decorators import method_decorator
from decimal import Decimal

from apps.core.services import teacher_required
from apps.assessments.models import AssessmentComponent, AssessmentScore
from apps.enrollments.models import Enrollment
from apps.courses.offering_models import CourseOffering


@method_decorator(login_required, name='dispatch')
@method_decorator(teacher_required, name='dispatch')
class ComponentMarksEntryView(View):
    """Enter marks for a specific assessment component"""
    template_name = 'teacher_portal/marks/component_entry.html'
    
    def get(self, request, offering_pk, component_pk):
        offering = get_object_or_404(CourseOffering, pk=offering_pk, teacher=request.user.teacher_profile)
        component = get_object_or_404(AssessmentComponent, pk=component_pk, course_offering=offering)
        
        enrollments = Enrollment.objects.filter(
            course_offering=offering,
            enroll_status='enrolled'
        ).select_related('student', 'student__user')
        
        # Get existing scores
        scores = AssessmentScore.objects.filter(
            assessment_component=component,
            enrollment__in=enrollments
        ).select_related('enrollment')
        
        scores_dict = {s.enrollment_id: s.score for s in scores}
        
        return render(request, self.template_name, {
            'offering': offering,
            'component': component,
            'enrollments': enrollments,
            'scores_dict': scores_dict
        })
    
    def post(self, request, offering_pk, component_pk):
        offering = get_object_or_404(CourseOffering, pk=offering_pk, teacher=request.user.teacher_profile)
        component = get_object_or_404(AssessmentComponent, pk=component_pk, course_offering=offering)
        
        for key, value in request.POST.items():
            if key.startswith('score_'):
                enrollment_id = key.replace('score_', '')
                try:
                    enrollment = Enrollment.objects.get(pk=enrollment_id, course_offering=offering)
                    score = Decimal(value) if value else Decimal('0')
                    percentage = (score / Decimal(str(component.max_score))) * Decimal('100') if component.max_score > 0 else Decimal('0')
                    
                    AssessmentScore.objects.update_or_create(
                        enrollment=enrollment,
                        assessment_component=component,
                        defaults={
                            'score': score,
                            'percentage': percentage,
                            'status': 'entered',
                            'entered_by': request.user
                        }
                    )
                except (Enrollment.DoesNotExist, ValueError):
                    continue
        
        messages.success(request, _('Marks saved successfully'))
        return redirect('teacher_portal:teacher_component_marks', offering_pk=offering_pk, component_pk=component_pk)
