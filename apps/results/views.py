from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.db.models import Avg

from apps.core.services import admin_required, student_required
from apps.results.models import FinalResult
from apps.results.summary_models import SemesterSummary, CGPARecord
from apps.enrollments.models import Enrollment


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class PublishResultsView(View):
    """Publish final results for a course offering"""
    
    def post(self, request, offering_pk):
        from apps.courses.offering_models import CourseOffering
        offering = get_object_or_404(CourseOffering, pk=offering_pk)
        
        enrollments = Enrollment.objects.filter(
            course_offering=offering,
            enroll_status='enrolled'
        )
        
        published_count = 0
        for enrollment in enrollments:
            if hasattr(enrollment, 'final_result') and enrollment.final_result:
                # Use the publish method to ensure pipeline runs
                result = enrollment.final_result.publish(triggered_by=request.user)
                if result['success']:
                    published_count += 1
        
        messages.success(request, _('Published {count} results').format(count=published_count))
        return redirect('admin_portal:admin_offerings')


@method_decorator(login_required, name='dispatch')
@method_decorator(student_required, name='dispatch')
class StudentTranscriptView(View):
    """Generate student transcript"""
    template_name = 'student_portal/transcript/view.html'
    
    def get(self, request):
        student = request.user.student_profile
        
        # Get all published enrollments with results
        enrollments = Enrollment.objects.filter(
            student=student,
            final_result__is_published=True
        ).select_related(
            'course_offering',
            'course_offering__course',
            'course_offering__semester',
            'final_result'
        ).order_by('course_offering__semester__start_date')
        
        # Get semester summaries
        summaries = SemesterSummary.objects.filter(
            student=student
        ).select_related('semester').order_by('semester__start_date')
        
        return render(request, self.template_name, {
            'student': student,
            'enrollments': enrollments,
            'summaries': summaries,
            'cgpa': student.cgpa
        })
