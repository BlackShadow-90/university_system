from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from datetime import date

from apps.core.services import teacher_required
from apps.attendance.models import AttendanceRecord
from apps.enrollments.models import Enrollment
from apps.courses.offering_models import CourseOffering


@method_decorator(login_required, name='dispatch')
@method_decorator(teacher_required, name='dispatch')
class AttendanceEntryView(View):
    """Take attendance for a specific course offering"""
    template_name = 'teacher_portal/attendance/entry.html'
    
    def get(self, request, offering_pk):
        offering = get_object_or_404(CourseOffering, pk=offering_pk, teacher=request.user.teacher_profile)
        enrollments = Enrollment.objects.filter(
            course_offering=offering,
            enroll_status='enrolled'
        ).select_related('student', 'student__user')
        
        today = date.today()
        # Get today's attendance records if any
        attendance_today = AttendanceRecord.objects.filter(
            enrollment__course_offering=offering,
            attendance_date=today
        ).select_related('enrollment')
        
        attendance_dict = {a.enrollment_id: a.status for a in attendance_today}
        
        return render(request, self.template_name, {
            'offering': offering,
            'enrollments': enrollments,
            'today': today,
            'attendance_dict': attendance_dict
        })
    
    def post(self, request, offering_pk):
        offering = get_object_or_404(CourseOffering, pk=offering_pk, teacher=request.user.teacher_profile)
        attendance_date = request.POST.get('attendance_date', date.today())
        
        for key, value in request.POST.items():
            if key.startswith('status_'):
                enrollment_id = key.replace('status_', '')
                try:
                    enrollment = Enrollment.objects.get(pk=enrollment_id, course_offering=offering)
                    AttendanceRecord.objects.update_or_create(
                        enrollment=enrollment,
                        attendance_date=attendance_date,
                        defaults={
                            'status': value,
                            'recorded_by': request.user
                        }
                    )
                except Enrollment.DoesNotExist:
                    continue
        
        messages.success(request, _('Attendance recorded successfully'))
        return redirect('teacher_portal:teacher_attendance_entry', offering_pk=offering_pk)
