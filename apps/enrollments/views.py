from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator

from apps.core.services import admin_required, teacher_required, student_required
from apps.enrollments.models import Enrollment
from apps.courses.offering_models import CourseOffering
from apps.students.models import Student


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class EnrollmentListView(ListView):
    """List all enrollments"""
    model = Enrollment
    template_name = 'admin_portal/enrollments/list.html'
    context_object_name = 'enrollments'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = Enrollment.objects.select_related(
            'student', 'student__user', 'course_offering', 'course_offering__course'
        ).order_by('-enrolled_at')
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(enroll_status=status)
        
        # Filter by semester
        semester = self.request.GET.get('semester')
        if semester:
            queryset = queryset.filter(course_offering__semester_id=semester)
        
        return queryset



