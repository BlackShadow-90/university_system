from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.views import View
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.urls import reverse_lazy
from django.db.models import Count, Avg, Q
from django.utils.decorators import method_decorator
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ValidationError
from decimal import Decimal, ROUND_HALF_UP

from apps.core.services import admin_required, teacher_required, student_required
from apps.core.report_services import (
    TranscriptPDFGenerator, ReportGenerator
)
from apps.core.academic_services import GradeCalculationService
from apps.accounts.models import User, Role
from apps.students.models import Student
from apps.teachers.models import Teacher
from apps.departments.models import Department
from apps.programs.models import Program
from apps.semesters.models import Semester
from apps.courses.models import Course
from apps.courses.offering_models import CourseOffering
from apps.enrollments.models import Enrollment
from apps.warnings.models import EarlyWarningResult, EarlyWarningRule
from apps.announcements.models import Announcement
from apps.auditlogs.models import AuditLog
from apps.settings_app.models import GradePolicy
from apps.assessments.models import AssessmentComponent


def create_audit_log(request, action, module, entity_type, entity_id, entity_repr, description, before_data=None, after_data=None):
    """Helper function to create audit log entries"""
    try:
        AuditLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action=action,
            module=module,
            entity_type=entity_type,
            entity_id=str(entity_id) if entity_id else '',
            entity_repr=entity_repr,
            description=description,
            before_data=before_data or {},
            after_data=after_data or {},
            ip_address=getattr(request, 'audit_ip', None),
            user_agent=getattr(request, 'audit_user_agent', '')
        )
    except Exception:
        pass  # Don't let audit logging break the main functionality


# ============================================
# Admin Portal Views
# ============================================

@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class AdminDashboardView(TemplateView):
    """Admin dashboard with overview statistics"""
    template_name = 'admin_portal/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistics
        context['total_students'] = Student.objects.filter(status='active').count()
        context['total_teachers'] = Teacher.objects.filter(status='active').count()
        context['total_departments'] = Department.objects.filter(status='active').count()
        context['total_courses'] = Course.objects.filter(status='active').count()
        
        # Active semester
        context['active_semester'] = Semester.objects.filter(is_active=True).first()
        
        # Warning statistics
        warning_results = EarlyWarningResult.objects.filter(
            semester=context['active_semester']
        ) if context['active_semester'] else EarlyWarningResult.objects.none()
        
        context['students_at_risk'] = warning_results.filter(
            warning_level__in=['orange', 'red']
        ).count()
        context['critical_warnings'] = warning_results.filter(
            warning_level='red'
        ).count()
        
        # Recent data
        context['recent_students'] = Student.objects.select_related('user').order_by('-created_at')[:5]
        context['recent_enrollments'] = Enrollment.objects.select_related('student', 'course_offering').order_by('-enrolled_at')[:5]
        context['recent_announcements'] = Announcement.objects.filter(is_active=True).order_by('-created_at')[:5]
        
        return context


# User Management Views
@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class UserListView(ListView):
    """List all users"""
    model = User
    template_name = 'admin_portal/users/list.html'
    context_object_name = 'users'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = User.objects.select_related('role').all()
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(full_name_en__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search)
            )
        
        # Filter by role
        role = self.request.GET.get('role')
        if role:
            queryset = queryset.filter(role__code=role)
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['roles'] = Role.objects.all()
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class UserCreateView(CreateView):
    """Create new user"""
    model = User
    template_name = 'admin_portal/users/form.html'
    fields = ['full_name_en', 'full_name_zh', 'email', 'phone', 'role', 'status', 'is_staff']
    
    def get_success_url(self):
        messages.success(self.request, _('User created successfully'))
        return reverse_lazy('admin_portal:admin_users')


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class UserDetailView(DetailView):
    """View user details"""
    model = User
    template_name = 'admin_portal/users/detail.html'
    context_object_name = 'user_obj'


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class UserUpdateView(UpdateView):
    """Update user"""
    model = User
    template_name = 'admin_portal/users/form.html'
    fields = ['full_name_en', 'full_name_zh', 'email', 'phone', 'role', 'status', 'is_staff']
    
    def get_success_url(self):
        messages.success(self.request, _('User updated successfully'))
        return reverse_lazy('admin_portal:admin_users')


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class UserDeleteView(DeleteView):
    """Delete user"""
    model = User
    template_name = 'admin_portal/users/confirm_delete.html'
    context_object_name = 'user_obj'
    
    def get_success_url(self):
        messages.success(self.request, _('User deleted successfully'))
        return reverse_lazy('admin_portal:admin_users')


# Student Management Views
@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class StudentListView(ListView):
    """List all students with search, filtering, and sorting"""
    model = Student
    template_name = 'admin_portal/students/list.html'
    context_object_name = 'students'
    paginate_by = 25
    
    def get_paginate_by(self, queryset):
        """Allow dynamic pagination"""
        per_page = self.request.GET.get('per_page')
        if per_page and per_page.isdigit():
            return int(per_page)
        return super().get_paginate_by(queryset)
    
    def get_queryset(self):
        queryset = Student.objects.select_related('user', 'department', 'program')
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(student_no__icontains=search) |
                Q(user__full_name_en__icontains=search) |
                Q(user__full_name_zh__icontains=search) |
                Q(user__email__icontains=search)
            )
        
        # Status filter
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Department filter
        department_id = self.request.GET.get('department')
        if department_id and department_id.isdigit():
            queryset = queryset.filter(department_id=int(department_id))
        
        # Batch year filter
        batch_year = self.request.GET.get('batch')
        if batch_year and batch_year.isdigit():
            queryset = queryset.filter(batch_year=int(batch_year))
        
        # Sorting
        sort = self.request.GET.get('sort')
        if sort:
            if sort == 'student_no':
                queryset = queryset.order_by('student_no')
            elif sort == 'name':
                queryset = queryset.order_by('user__full_name_en')
            elif sort == 'batch_year':
                queryset = queryset.order_by('-batch_year')
            elif sort == 'cgpa':
                queryset = queryset.order_by('-cgpa')
            else:
                queryset = queryset.order_by('student_no')
        else:
            queryset = queryset.order_by('student_no')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add departments for filter dropdown
        from apps.departments.models import Department
        context['departments'] = Department.objects.filter(status='active').order_by('name_en')
        
        # Add current filter values for form persistence
        context['current_filters'] = {
            'search': self.request.GET.get('search', ''),
            'status': self.request.GET.get('status', ''),
            'department': self.request.GET.get('department', ''),
            'batch': self.request.GET.get('batch', ''),
            'per_page': self.request.GET.get('per_page', '25'),
            'sort': self.request.GET.get('sort', ''),
        }
        
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class StudentCreateView(CreateView):
    """Create new student with User account"""
    model = Student
    template_name = 'admin_portal/students/form.html'
    fields = ['student_no', 'department', 'program', 'current_semester', 'batch_year', 
              'gender', 'date_of_birth', 'guardian_name', 'guardian_phone', 'status']
    
    def get_context_data(self, **kwargs):
        from apps.teachers.models import Teacher
        context = super().get_context_data(**kwargs)
        context['departments'] = Department.objects.filter(status='active').order_by('name_en')
        context['programs'] = Program.objects.filter(status='active').order_by('name_en')
        context['semesters'] = Semester.objects.filter(is_active=True).order_by('-start_date')
        context['teachers'] = Teacher.objects.select_related('user').order_by('teacher_no')
        return context
    
    def form_valid(self, form):
        from apps.accounts.models import User, Role
        from django.contrib.auth.hashers import make_password
        import random
        import string
        
        # Get form data
        email = self.request.POST.get('email')
        full_name_en = self.request.POST.get('full_name_en')
        full_name_zh = self.request.POST.get('full_name_zh')
        phone = self.request.POST.get('phone')
        
        # Validate required fields
        if not email or not full_name_en:
            messages.error(self.request, _('Email and Full Name (English) are required'))
            return self.form_invalid(form)
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            messages.error(self.request, _('A user with this email already exists'))
            return self.form_invalid(form)
        
        # Get student role
        try:
            student_role = Role.objects.get(code='student')
        except Role.DoesNotExist:
            messages.error(self.request, _('Student role not found. Please create roles first.'))
            return self.form_invalid(form)
        
        # Check for form errors before proceeding
        if not form.is_valid():
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(self.request, f"{field}: {error}")
            return self.form_invalid(form)
        
        # Generate a random password
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        
        # Create User with PENDING status - activation is separate step
        user = User.objects.create(
            email=email,
            full_name_en=full_name_en,
            full_name_zh=full_name_zh or '',
            phone=phone or '',
            password=make_password(password),
            role=student_role,
            status='pending'
        )
        
        # Save student form with the user
        student = form.save(commit=False)
        student.user = user
        student.save()
        
        # Save extra fields from POST
        student.nationality = self.request.POST.get('nationality', '')
        student.id_number = self.request.POST.get('id_number', '')
        student.guardian_email = self.request.POST.get('guardian_email', '')
        student.guardian_relationship = self.request.POST.get('guardian_relationship', '')
        student.admission_date = self.request.POST.get('admission_date') or None
        student.expected_graduation = self.request.POST.get('expected_graduation') or None
        
        # Save advisor if provided
        advisor_id = self.request.POST.get('advisor')
        if advisor_id:
            from apps.teachers.models import Teacher
            try:
                student.advisor = Teacher.objects.get(pk=advisor_id)
            except Teacher.DoesNotExist:
                pass
        
        student.save()
        
        # Create audit log
        create_audit_log(
            self.request,
            action='create',
            module='Students',
            entity_type='Student',
            entity_id=student.pk,
            entity_repr=student.user.get_full_name(),
            description=f'Created student {student.student_no} - {student.user.get_full_name()}',
            after_data={'student_no': student.student_no, 'email': email}
        )
        
        messages.success(
            self.request, 
            _('Student info saved. Account pending activation. Use Activate Accounts page to activate.') 
        )
        return redirect(self.get_success_url())
    
    def get_success_url(self):
        return reverse_lazy('admin_portal:admin_students')


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class StudentDetailView(DetailView):
    """View student details"""
    model = Student
    template_name = 'admin_portal/students/detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.object
        
        # Get student enrollments with course details and marks
        from apps.enrollments.models import Enrollment
        from apps.assessments.models import AssessmentComponent, AssessmentScore
        
        enrollments = Enrollment.objects.filter(
            student=student
        ).select_related(
            'course_offering',
            'course_offering__course',
            'course_offering__semester',
            'course_offering__teacher',
            'final_result'
        ).order_by('-course_offering__semester__start_date')
        
        # Build enrollment data with component scores
        enrollment_data = []
        for enrollment in enrollments:
            # Get assessment components and scores for this enrollment
            components = AssessmentComponent.objects.filter(
                course_offering=enrollment.course_offering
            ).order_by('order')
            
            component_scores = []
            for component in components:
                score = AssessmentScore.objects.filter(
                    enrollment=enrollment,
                    assessment_component=component
                ).first()
                component_scores.append({
                    'component': component,
                    'score': score
                })
            
            enrollment_data.append({
                'enrollment': enrollment,
                'component_scores': component_scores
            })
        
        context['enrollment_data'] = enrollment_data
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class StudentUpdateView(UpdateView):
    """Update student"""
    model = Student
    template_name = 'admin_portal/students/form.html'
    fields = ['student_no', 'department', 'program', 'current_semester', 'batch_year', 
              'gender', 'date_of_birth', 'nationality', 'id_number', 'guardian_name', 
              'guardian_phone', 'guardian_email', 'guardian_relationship', 'advisor',
              'admission_date', 'expected_graduation', 'status']
    
    def get_context_data(self, **kwargs):
        from apps.teachers.models import Teacher
        context = super().get_context_data(**kwargs)
        context['departments'] = Department.objects.filter(status='active').order_by('name_en')
        context['programs'] = Program.objects.filter(status='active').order_by('name_en')
        context['semesters'] = Semester.objects.filter(is_active=True).order_by('-start_date')
        context['teachers'] = Teacher.objects.select_related('user').order_by('teacher_no')
        return context
    
    def get_success_url(self):
        messages.success(self.request, _('Student updated successfully'))
        return reverse_lazy('admin_portal:admin_students')


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class StudentDeleteView(DeleteView):
    """Delete student"""
    model = Student
    template_name = 'admin_portal/students/confirm_delete.html'
    
    def get_success_url(self):
        messages.success(self.request, _('Student deleted successfully'))
        return reverse_lazy('admin_portal:admin_students')


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class StudentImportView(View):
    """Import students from CSV/Excel"""
    template_name = 'admin_portal/students/import.html'
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        # Import logic would go here
        messages.success(request, _('Students imported successfully'))
        return redirect('admin_portal:admin_students')


# Teacher Management Views
@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class TeacherListView(ListView):
    """List all teachers"""
    model = Teacher
    template_name = 'admin_portal/teachers/list.html'
    context_object_name = 'teachers'
    paginate_by = 25
    
    def get_queryset(self):
        return Teacher.objects.select_related('user', 'department').order_by('teacher_no')


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class TeacherCreateView(CreateView):
    """Create new teacher with User account"""
    model = Teacher
    template_name = 'admin_portal/teachers/form.html'
    fields = ['teacher_no', 'department', 'title', 'specialization', 'office_location', 
              'office_hours', 'bio', 'join_date', 'status']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = Department.objects.filter(status='active').order_by('name_en')
        return context
    
    def form_valid(self, form):
        from apps.accounts.models import User, Role
        from django.contrib.auth.hashers import make_password
        import random
        import string
        
        # Get form data
        email = self.request.POST.get('email')
        full_name_en = self.request.POST.get('full_name_en')
        full_name_zh = self.request.POST.get('full_name_zh')
        phone = self.request.POST.get('phone')
        
        # Validate required fields
        if not email or not full_name_en:
            messages.error(self.request, _('Email and Full Name (English) are required'))
            return self.form_invalid(form)
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            messages.error(self.request, _('A user with this email already exists'))
            return self.form_invalid(form)
        
        # Get teacher role
        try:
            teacher_role = Role.objects.get(code='teacher')
        except Role.DoesNotExist:
            messages.error(self.request, _('Teacher role not found. Please create roles first.'))
            return self.form_invalid(form)
        
        # Generate a random password
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        
        # Create User with PENDING status - activation is separate step
        user = User.objects.create(
            email=email,
            full_name_en=full_name_en,
            full_name_zh=full_name_zh or '',
            phone=phone or '',
            password=make_password(password),
            role=teacher_role,
            status='pending'
        )
        
        # Save teacher form with the user
        teacher = form.save(commit=False)
        teacher.user = user
        teacher.save()
        
        # Save extra fields from POST
        teacher.office_location = self.request.POST.get('office_location', '')
        teacher.office_hours = self.request.POST.get('office_hours', '')
        teacher.bio = self.request.POST.get('bio', '')
        teacher.save()
        
        # Create audit log
        create_audit_log(
            self.request,
            action='create',
            module='Teachers',
            entity_type='Teacher',
            entity_id=teacher.pk,
            entity_repr=teacher.user.get_full_name(),
            description=f'Created teacher {teacher.teacher_no} - {teacher.user.get_full_name()}',
            after_data={'teacher_no': teacher.teacher_no, 'email': email}
        )
        
        messages.success(
            self.request, 
            _('Teacher info saved. Account pending activation. Use Activate Accounts page to activate.') 
        )
        return redirect(self.get_success_url())
    
    def get_success_url(self):
        return reverse_lazy('admin_portal:admin_teachers')


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class TeacherDetailView(DetailView):
    """View teacher details"""
    model = Teacher
    template_name = 'admin_portal/teachers/detail.html'


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class TeacherUpdateView(UpdateView):
    """Update teacher"""
    model = Teacher
    template_name = 'admin_portal/teachers/form.html'
    fields = ['teacher_no', 'department', 'title', 'specialization', 'office_location', 
              'office_hours', 'bio', 'join_date', 'status']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = Department.objects.filter(status='active').order_by('name_en')
        return context
    
    def get_success_url(self):
        messages.success(self.request, _('Teacher updated successfully'))
        return reverse_lazy('admin_portal:admin_teachers')


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class TeacherDeleteView(DeleteView):
    """Delete teacher"""
    model = Teacher
    template_name = 'admin_portal/teachers/confirm_delete.html'
    
    def get_success_url(self):
        messages.success(self.request, _('Teacher deleted successfully'))
        return reverse_lazy('admin_portal:admin_teachers')


# Department Management Views
@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class DepartmentListView(ListView):
    """List all departments"""
    model = Department
    template_name = 'admin_portal/departments/list.html'
    context_object_name = 'departments'


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class DepartmentCreateView(CreateView):
    """Create new department"""
    model = Department
    template_name = 'admin_portal/departments/form.html'
    fields = '__all__'
    success_url = reverse_lazy('admin_portal:admin_departments')


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class DepartmentUpdateView(UpdateView):
    """Update department"""
    model = Department
    template_name = 'admin_portal/departments/form.html'
    fields = '__all__'
    success_url = reverse_lazy('admin_portal:admin_departments')


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class DepartmentDeleteView(DeleteView):
    """Delete department"""
    model = Department
    template_name = 'admin_portal/departments/confirm_delete.html'
    success_url = reverse_lazy('admin_portal:admin_departments')
    
    def form_valid(self, form):
        from django.db.models.deletion import ProtectedError
        try:
            return super().form_valid(form)
        except ProtectedError:
            messages.error(
                self.request, 
                _('Cannot delete department: It is being used by courses, programs, or students. Please reassign or delete those items first.')
            )
            return redirect('admin_portal:admin_departments')


# Program Management Views
@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class ProgramListView(ListView):
    """List all programs"""
    model = Program
    template_name = 'admin_portal/programs/list.html'
    context_object_name = 'programs'


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class ProgramCreateView(CreateView):
    """Create new program"""
    model = Program
    template_name = 'admin_portal/programs/form.html'
    fields = '__all__'
    success_url = reverse_lazy('admin_portal:admin_programs')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = Department.objects.filter(status='active').order_by('name_en')
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class ProgramUpdateView(UpdateView):
    """Update program"""
    model = Program
    template_name = 'admin_portal/programs/form.html'
    fields = '__all__'
    success_url = reverse_lazy('admin_portal:admin_programs')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = Department.objects.filter(status='active').order_by('name_en')
        return context


# Semester Management Views
@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class SemesterListView(ListView):
    """List all semesters"""
    model = Semester
    template_name = 'admin_portal/semesters/list.html'
    context_object_name = 'semesters'


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class SemesterCreateView(CreateView):
    """Create new semester"""
    model = Semester
    template_name = 'admin_portal/semesters/form.html'
    fields = '__all__'
    success_url = reverse_lazy('admin_portal:admin_semesters')


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class SemesterUpdateView(UpdateView):
    """Update semester"""
    model = Semester
    template_name = 'admin_portal/semesters/form.html'
    fields = '__all__'
    success_url = reverse_lazy('admin_portal:admin_semesters')


# Course Management Views
@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class CourseListView(ListView):
    """List all courses"""
    model = Course
    template_name = 'admin_portal/courses/list.html'
    context_object_name = 'courses'


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class CourseCreateView(CreateView):
    """Create new course"""
    model = Course
    template_name = 'admin_portal/courses/form.html'
    fields = '__all__'
    success_url = reverse_lazy('admin_portal:admin_courses')


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class CourseUpdateView(UpdateView):
    """Update course"""
    model = Course
    template_name = 'admin_portal/courses/form.html'
    fields = '__all__'
    success_url = reverse_lazy('admin_portal:admin_courses')


# Course Offering Management Views
@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class CourseOfferingListView(ListView):
    """List all course offerings grouped by course"""
    model = CourseOffering
    template_name = 'admin_portal/offerings/list.html'
    context_object_name = 'offerings'
    
    def get_queryset(self):
        return CourseOffering.objects.select_related(
            'course', 'semester', 'teacher', 'teacher__user'
        ).order_by('course__code', 'semester__start_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Group offerings by course
        from collections import defaultdict
        grouped_offerings = defaultdict(list)
        
        for offering in context['offerings']:
            grouped_offerings[offering.course].append(offering)
        
        # Convert to sorted list
        context['grouped_offerings'] = []
        for course in sorted(grouped_offerings.keys(), key=lambda c: c.code):
            context['grouped_offerings'].append({
                'course': course,
                'offerings': grouped_offerings[course]
            })
        
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class CourseOfferingCreateView(CreateView):
    """Create new course offering"""
    model = CourseOffering
    template_name = 'admin_portal/offerings/form.html'
    fields = '__all__'
    success_url = reverse_lazy('admin_portal:admin_offerings')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['courses'] = Course.objects.filter(status='active').order_by('code')
        context['semesters'] = Semester.objects.all().order_by('-start_date')
        context['teachers'] = Teacher.objects.select_related('user').order_by('teacher_no')
        return context
    
    def get_success_url(self):
        messages.success(self.request, _('Course offering created successfully'))
        return reverse_lazy('admin_portal:admin_offerings')


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class CourseOfferingUpdateView(UpdateView):
    """Update course offering"""
    model = CourseOffering
    template_name = 'admin_portal/offerings/form.html'
    fields = '__all__'
    success_url = reverse_lazy('admin_portal:admin_offerings')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['courses'] = Course.objects.filter(status='active').order_by('code')
        context['semesters'] = Semester.objects.all().order_by('-start_date')
        context['teachers'] = Teacher.objects.select_related('user').order_by('teacher_no')
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class CourseOfferingDeleteView(DeleteView):
    """Delete course offering"""
    model = CourseOffering
    template_name = 'admin_portal/offerings/confirm_delete.html'
    
    def get_success_url(self):
        messages.success(self.request, _('Course offering deleted successfully'))
        return reverse_lazy('admin_portal:admin_offerings')


# Assessment Component Management Views
@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class OfferingComponentListView(DetailView):
    """List assessment components for a course offering"""
    model = CourseOffering
    template_name = 'admin_portal/offerings/components/list.html'
    pk_url_kwarg = 'pk'
    context_object_name = 'offering'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['components'] = self.object.assessment_components.all().order_by('order')
        # Calculate total weight
        total_weight = sum(c.weight_percentage for c in context['components'])
        context['total_weight'] = total_weight
        context['weight_valid'] = total_weight == 100
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class OfferingComponentCreateView(CreateView):
    """Add assessment component to a course offering"""
    model = AssessmentComponent
    template_name = 'admin_portal/offerings/components/form.html'
    fields = ['name', 'assessment_type', 'weight_percentage', 'max_score', 'due_date', 'description', 'order']
    
    def dispatch(self, request, *args, **kwargs):
        self.offering = get_object_or_404(CourseOffering, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['offering'] = self.offering
        context['is_create'] = True
        # Get existing components for reference
        context['existing_components'] = self.offering.assessment_components.all().order_by('order')
        # Calculate current total weight
        context['current_total_weight'] = sum(c.weight_percentage for c in context['existing_components'])
        return context
    
    def form_valid(self, form):
        form.instance.course_offering = self.offering
        messages.success(self.request, _('Assessment component added successfully'))
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('admin_portal:admin_offering_components', kwargs={'pk': self.offering.pk})


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class OfferingComponentUpdateView(UpdateView):
    """Edit assessment component"""
    model = AssessmentComponent
    template_name = 'admin_portal/offerings/components/form.html'
    pk_url_kwarg = 'component_pk'
    fields = ['name', 'assessment_type', 'weight_percentage', 'max_score', 'due_date', 'description', 'order', 'is_published']
    
    def dispatch(self, request, *args, **kwargs):
        self.offering = get_object_or_404(CourseOffering, pk=kwargs['offering_pk'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['offering'] = self.offering
        context['is_create'] = False
        context['existing_components'] = self.offering.assessment_components.all().order_by('order')
        context['current_total_weight'] = sum(c.weight_percentage for c in context['existing_components'] if c.pk != self.object.pk)
        return context
    
    def form_valid(self, form):
        messages.success(self.request, _('Assessment component updated successfully'))
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('admin_portal:admin_offering_components', kwargs={'pk': self.offering.pk})


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class OfferingComponentDeleteView(DeleteView):
    """Delete assessment component"""
    model = AssessmentComponent
    template_name = 'admin_portal/offerings/components/confirm_delete.html'
    pk_url_kwarg = 'component_pk'
    context_object_name = 'component'
    
    def dispatch(self, request, *args, **kwargs):
        self.offering = get_object_or_404(CourseOffering, pk=kwargs['offering_pk'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['offering'] = self.offering
        return context
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, _('Assessment component deleted successfully'))
        return super().delete(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse_lazy('admin_portal:admin_offering_components', kwargs={'pk': self.offering.pk})


# Enrollment Management Views
@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class EnrollmentListView(ListView):
    """List all enrollments grouped by semester and course"""
    model = Enrollment
    template_name = 'admin_portal/enrollments/list.html'
    context_object_name = 'enrollments'
    
    def get_queryset(self):
        return Enrollment.objects.select_related(
            'student', 'student__user', 'course_offering', 'course_offering__course', 
            'course_offering__semester'
        ).order_by('course_offering__semester__academic_year', 'course_offering__course__code', 'student__student_no')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Group enrollments by semester, then by course
        from collections import defaultdict
        
        # First group by semester
        semester_groups = defaultdict(lambda: defaultdict(list))
        
        for enrollment in context['enrollments']:
            semester = enrollment.course_offering.semester
            course = enrollment.course_offering.course
            semester_groups[semester][course].append(enrollment)
        
        # Convert to sorted structure
        grouped_enrollments = []
        for semester in sorted(semester_groups.keys(), key=lambda s: (s.academic_year, s.semester_type)):
            course_list = []
            for course in sorted(semester_groups[semester].keys(), key=lambda c: c.code):
                course_list.append({
                    'course': course,
                    'enrollments': semester_groups[semester][course]
                })
            
            grouped_enrollments.append({
                'semester': semester,
                'courses': course_list
            })
        
        context['grouped_enrollments'] = grouped_enrollments
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class BulkEnrollmentView(View):
    """Bulk enrollment view"""
    template_name = 'admin_portal/enrollments/bulk.html'
    
    def get(self, request):
        # Get available courses and students for the form
        from apps.courses.offering_models import CourseOffering
        from apps.students.models import Student
        
        offerings = CourseOffering.objects.filter(
            status='open'
        ).select_related('course', 'semester', 'teacher', 'teacher__user').order_by('course__code')
        
        # Build course data dict for JavaScript
        course_offerings_data = {}
        for offering in offerings:
            course_offerings_data[str(offering.pk)] = {
                'course': offering.course.title_en,
                'code': offering.course.code,
                'semester': str(offering.semester),
                'credits': str(offering.course.credit_hours),
                'instructor': offering.teacher.user.get_full_name() if offering.teacher and offering.teacher.user else 'Not assigned'
            }
        
        context = {
            'course_offerings': offerings,
            'course_offerings_data': course_offerings_data,
            'students': Student.objects.filter(
                status='active'
            ).select_related('user', 'department', 'program').order_by('student_no')
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        from apps.enrollments.models import Enrollment
        from apps.courses.offering_models import CourseOffering
        from apps.students.models import Student
        
        course_offering_id = request.POST.get('course_offering')
        student_ids = request.POST.getlist('students')
        
        if not course_offering_id or not student_ids:
            messages.error(request, _('Please select a course and at least one student'))
            return redirect('admin_portal:admin_bulk_enrollment')
        
        try:
            course_offering = CourseOffering.objects.get(pk=course_offering_id)
            enrolled_count = 0
            skipped_count = 0
            
            for student_id in student_ids:
                student = Student.objects.get(pk=student_id)
                
                # Check if already enrolled
                if Enrollment.objects.filter(
                    student=student,
                    course_offering=course_offering
                ).exists():
                    skipped_count += 1
                    continue
                
                # Create enrollment
                Enrollment.objects.create(
                    student=student,
                    course_offering=course_offering,
                    enroll_status='enrolled'
                )
                enrolled_count += 1
            
            if enrolled_count > 0:
                messages.success(
                    request, 
                    _('Successfully enrolled %(count)d students in %(course)s') % {
                        'count': enrolled_count,
                        'course': course_offering.course.title_en
                    }
                )
            
            if skipped_count > 0:
                messages.warning(
                    request,
                    _('Skipped %(count)d students who were already enrolled') % {'count': skipped_count}
                )
                
        except Exception as e:
            messages.error(request, _('Error during bulk enrollment: %(error)s') % {'error': str(e)})
        
        return redirect('admin_portal:admin_enrollments')


# Warning Management Views
@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class WarningListView(ListView):
    """List all warning results"""
    model = EarlyWarningResult
    template_name = 'admin_portal/warnings/list.html'
    context_object_name = 'warnings'


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class WarningRuleListView(ListView):
    """List warning rules"""
    model = EarlyWarningRule
    template_name = 'admin_portal/warnings/rules.html'
    context_object_name = 'rules'


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class CalculateWarningsView(View):
    """Calculate warnings for all students using algorithm"""
    
    def post(self, request):
        from apps.students.models import Student
        from apps.semesters.models import Semester
        from apps.warnings.risk_service import RiskCalculationService
        from .academic_services import WarningManagementService
        
        # Get active semester
        semester = Semester.objects.filter(is_active=True).first()
        if not semester:
            messages.error(request, _('No active semester found'))
            return redirect('admin_portal:admin_warnings')
        
        # Ensure default rules exist via service
        WarningManagementService.ensure_default_rules_exist()
        
        # Get all active students with enrollments
        students = Student.objects.filter(
            enrollments__course_offering__semester=semester
        ).distinct()
        
        calculated_count = 0
        warning_count = 0
        
        for student in students:
            try:
                result = RiskCalculationService.generate_warning_for_student(student, semester)
                if result:
                    calculated_count += 1
                    if result.warning_level in ['orange', 'red']:
                        warning_count += 1
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error calculating warning for {student}: {e}")
        
        messages.success(
            request, 
            _('Warnings calculated for %(count)d students. %(warnings)d students have warnings.') % {
                'count': calculated_count,
                'warnings': warning_count
            }
        )
        return redirect('admin_portal:admin_warnings')


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class ManualWarningCreateView(View):
    """Manually create warning for a specific student"""
    template_name = 'admin_portal/warnings/manual_form.html'
    
    def get(self, request):
        from apps.students.models import Student
        from apps.semesters.models import Semester
        
        # Get student from query param if editing
        student_id = request.GET.get('student')
        student = None
        if student_id:
            student = Student.objects.filter(pk=student_id).first()
        
        context = {
            'students': Student.objects.filter(status='active').select_related('user').order_by('student_no'),
            'semesters': Semester.objects.all().order_by('-start_date'),
            'selected_student': student,
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        from apps.warnings.models import EarlyWarningResult
        from apps.students.models import Student
        from apps.semesters.models import Semester
        from .academic_services import WarningManagementService
        
        student_id = request.POST.get('student')
        semester_id = request.POST.get('semester')
        warning_level = request.POST.get('warning_level')
        reason = request.POST.get('reason')
        
        if not all([student_id, semester_id, warning_level, reason]):
            messages.error(request, _('All fields are required'))
            return self.get(request)
        
        try:
            student = Student.objects.get(pk=student_id)
            semester = Semester.objects.get(pk=semester_id)
            
            # Use service to create manual warning
            result = WarningManagementService.create_manual_warning(
                student=student,
                semester=semester,
                warning_level=warning_level,
                reason=reason,
                created_by=request.user.get_full_name()
            )
            
            messages.success(
                request, 
                _('Warning assigned to %(student)s for %(semester)s') % {
                    'student': student.user.get_full_name(),
                    'semester': semester
                }
            )
            return redirect('admin_portal:admin_warnings')
            
        except Student.DoesNotExist:
            messages.error(request, _('Student not found'))
        except Semester.DoesNotExist:
            messages.error(request, _('Semester not found'))
        
        return self.get(request)


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class ClearWarningView(View):
    """Clear/resolve warning for a student"""
    
    def post(self, request, pk):
        from apps.warnings.models import EarlyWarningResult
        from .academic_services import WarningManagementService
        
        warning = get_object_or_404(EarlyWarningResult, pk=pk)
        
        # Use service to clear warning
        WarningManagementService.clear_warning(
            warning=warning,
            cleared_by=request.user.get_full_name()
        )
        
        messages.success(
            request, 
            _('Warning cleared for %(student)s') % {'student': warning.student.user.get_full_name()}
        )
        return redirect('admin_portal:admin_warnings')


# Announcement Management Views
@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class AnnouncementListView(ListView):
    """List all announcements"""
    model = Announcement
    template_name = 'admin_portal/announcements/list.html'
    context_object_name = 'announcements'


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class AnnouncementCreateView(CreateView):
    """Create new announcement"""
    model = Announcement
    template_name = 'admin_portal/announcements/form.html'
    fields = '__all__'
    success_url = reverse_lazy('admin_portal:admin_announcements')
    
    def form_valid(self, form):
        # Set published_by to current user
        form.instance.published_by = self.request.user
        # Set published_at to now if not provided
        if not form.instance.published_at:
            from django.utils import timezone
            form.instance.published_at = timezone.now()
        
        # Save the announcement first
        response = super().form_valid(form)
        
        # Create audit log
        create_audit_log(
            self.request,
            action='create',
            module='Announcements',
            entity_type='Announcement',
            entity_id=self.object.pk,
            entity_repr=self.object.title_en,
            description=f'Created announcement: {self.object.title_en}',
            after_data={'title_en': self.object.title_en, 'priority': self.object.priority}
        )
        
        messages.success(self.request, _('Announcement created successfully'))
        return response


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class AnnouncementUpdateView(UpdateView):
    """Update announcement"""
    model = Announcement
    template_name = 'admin_portal/announcements/form.html'
    fields = '__all__'
    success_url = reverse_lazy('admin_portal:admin_announcements')
    
    def form_valid(self, form):
        messages.success(self.request, _('Announcement updated successfully'))
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class AnnouncementDeleteView(View):
    """Delete announcement"""
    
    def post(self, request, pk):
        from apps.announcements.models import Announcement
        announcement = get_object_or_404(Announcement, pk=pk)
        title = announcement.title_en
        announcement.delete()
        messages.success(request, _('Announcement "%(title)s" deleted successfully') % {'title': title})
        return redirect('admin_portal:admin_announcements')


# Reports Views
@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class ReportsView(TemplateView):
    """Reports dashboard"""
    template_name = 'admin_portal/reports/dashboard.html'


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class StudentReportView(View):
    """Student report view"""
    template_name = 'admin_portal/reports/students.html'
    
    def get(self, request):
        return render(request, self.template_name)


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class GradeReportView(View):
    """Grade report view"""
    template_name = 'admin_portal/reports/grades.html'
    
    def get(self, request):
        return render(request, self.template_name)


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class WarningReportView(View):
    """Warning report view"""
    template_name = 'admin_portal/reports/warnings.html'
    
    def get(self, request):
        return render(request, self.template_name)


# Settings Views
@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class SettingsView(TemplateView):
    """System settings view"""
    template_name = 'admin_portal/settings/dashboard.html'


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class GradePolicyView(TemplateView):
    """Grade policy settings management"""
    template_name = 'admin_portal/settings/grade_policy.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all grade policies
        policies = GradePolicy.objects.all().order_by('-is_default', 'name')
        context['policies'] = policies
        context['default_policy'] = GradePolicy.objects.filter(is_default=True).first()
        
        # Serialize policies for JavaScript
        import json
        policies_data = []
        for policy in policies:
            policies_data.append({
                'pk': policy.pk,
                'fields': {
                    'name': policy.name,
                    'max_gpa': str(policy.max_gpa),
                    'passing_grade_point': str(policy.passing_grade_point),
                    'gpa_warning_threshold': str(policy.gpa_warning_threshold),
                    'cgpa_warning_threshold': str(policy.cgpa_warning_threshold),
                    'attendance_warning_threshold': str(policy.attendance_warning_threshold),
                    'gpa_drop_warning_threshold': str(policy.gpa_drop_warning_threshold),
                    'description': policy.description,
                    'is_default': policy.is_default,
                }
            })
        context['policies_json'] = json.dumps(policies_data)
        
        # Handle form data from session (for validation errors)
        if 'form_data' in self.request.session:
            form_data = self.request.session.pop('form_data')
            policy_id = self.request.session.pop('policy_id', None)
            action = self.request.session.pop('action', 'create')
            
            from apps.settings_app.forms import GradePolicyForm
            if action == 'update' and policy_id:
                policy = GradePolicy.objects.filter(pk=policy_id).first()
                form = GradePolicyForm(form_data, instance=policy)
            else:
                form = GradePolicyForm(form_data)
            
            context['form'] = form
            context['form_action'] = action
            context['editing_policy_id'] = policy_id
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle grade policy creation/update"""
        from apps.settings_app.models import GradePolicy
        from apps.settings_app.forms import GradePolicyForm
        from django.contrib import messages
        
        policy_id = request.POST.get('policy_id')
        action = request.POST.get('action')
        
        if action in ['create', 'update']:
            if action == 'update' and policy_id:
                policy = GradePolicy.objects.get(pk=policy_id)
                form = GradePolicyForm(request.POST, instance=policy)
            else:
                form = GradePolicyForm(request.POST)
            
            if form.is_valid():
                policy = form.save()
                if action == 'create':
                    messages.success(request, _('Grade policy created successfully'))
                else:
                    messages.success(request, _('Grade policy updated successfully'))
            else:
                # Add form errors to messages
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
                # Store form data in session to repopulate form
                request.session['form_data'] = request.POST
                if policy_id:
                    request.session['policy_id'] = policy_id
                    request.session['action'] = 'update'
                    
        elif action == 'delete' and policy_id:
            # Delete policy (if not default)
            policy = GradePolicy.objects.get(pk=policy_id)
            if policy.is_default:
                messages.error(request, _('Cannot delete default grade policy'))
            else:
                policy.delete()
                messages.success(request, _('Grade policy deleted successfully'))
        
        return redirect('admin_portal:grade_policy')


@method_decorator(login_required, name='dispatch')
@method_decorator(teacher_required, name='dispatch')
class TeacherFlagStudentView(View):
    """Teacher flags a student as at-risk"""
    
    def post(self, request, student_pk):
        from apps.warnings.models import EarlyWarningResult, EarlyWarningRule
        from apps.semesters.models import Semester
        from .academic_services import WarningManagementService
        
        student = get_object_or_404(Student, pk=student_pk)
        reason = request.POST.get('reason', 'Teacher concern')
        severity = request.POST.get('severity', 'orange')
        
        # Get active semester
        semester = Semester.objects.filter(is_active=True).first()
        if not semester:
            messages.error(request, _('No active semester found'))
            return redirect('teacher_portal:at_risk_students')
        
        # Use service to flag student
        result = WarningManagementService.flag_student_by_teacher(
            student=student,
            semester=semester,
            severity=severity,
            reason=reason,
            teacher_name=request.user.get_full_name()
        )
        
        messages.success(
            request, 
            _('Student %(student)s has been flagged as %(level)s') % {
                'student': student.user.get_full_name(),
                'level': severity
            }
        )
        return redirect('teacher_portal:at_risk_students')


# Audit Log Views
@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class AuditLogListView(ListView):
    """List audit logs"""
    model = AuditLog
    template_name = 'admin_portal/audit_logs/list.html'
    context_object_name = 'logs'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = AuditLog.objects.select_related('user').order_by('-created_at')
        
        # Filter by user
        user_filter = self.request.GET.get('user')
        if user_filter:
            queryset = queryset.filter(
                models.Q(user__full_name_en__icontains=user_filter) |
                models.Q(user__email__icontains=user_filter)
            )
        
        # Filter by action
        action_filter = self.request.GET.get('action')
        if action_filter:
            queryset = queryset.filter(action=action_filter)
        
        return queryset


# ============================================
# Teacher Portal Views
# ============================================

@method_decorator(login_required, name='dispatch')
@method_decorator(teacher_required, name='dispatch')
class TeacherDashboardView(TemplateView):
    """Teacher dashboard"""
    template_name = 'teacher_portal/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.request.user.teacher_profile
        
        # Get teacher's course offerings
        context['my_courses'] = CourseOffering.objects.filter(
            teacher=teacher,
            semester__is_active=True
        ).select_related('course', 'semester')[:6]
        
        # Count at-risk students in teacher's courses
        context['at_risk_count'] = EarlyWarningResult.objects.filter(
            student__enrollments__course_offering__teacher=teacher,
            warning_level__in=['orange', 'red']
        ).distinct().count()
        
        # Pending grade submissions
        context['pending_grades'] = CourseOffering.objects.filter(
            teacher=teacher,
            status='grading'
        ).count()
        
        # Latest announcements
        from apps.announcements.models import Announcement
        context['latest_announcements'] = Announcement.objects.filter(
            is_active=True
        ).select_related('published_by').order_by('-published_at')[:5]
        
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(teacher_required, name='dispatch')
class TeacherCourseListView(ListView):
    """List teacher's courses"""
    model = CourseOffering
    template_name = 'teacher_portal/courses/list.html'
    context_object_name = 'course_offerings'
    
    def get_queryset(self):
        return CourseOffering.objects.filter(
            teacher=self.request.user.teacher_profile,
            semester__is_active=True
        ).select_related('course', 'semester').order_by('-semester__start_date')


@method_decorator(login_required, name='dispatch')
@method_decorator(teacher_required, name='dispatch')
class TeacherCourseDetailView(DetailView):
    """View course details"""
    model = CourseOffering
    template_name = 'teacher_portal/courses/detail.html'
    pk_url_kwarg = 'offering_pk'
    context_object_name = 'offering'


@method_decorator(login_required, name='dispatch')
@method_decorator(teacher_required, name='dispatch')
class CourseStudentListView(ListView):
    """List students in a course"""
    model = Enrollment
    template_name = 'teacher_portal/courses/students.html'
    context_object_name = 'enrollments'
    
    def get_queryset(self):
        return Enrollment.objects.filter(
            course_offering_id=self.kwargs['offering_pk'],
            enroll_status='enrolled'
        ).select_related('student', 'student__user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['offering'] = get_object_or_404(CourseOffering, pk=self.kwargs['offering_pk'])
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(teacher_required, name='dispatch')
class TeacherAttendanceView(ListView):
    """List courses for attendance entry"""
    model = CourseOffering
    template_name = 'teacher_portal/attendance/list.html'
    context_object_name = 'course_offerings'
    
    def get_queryset(self):
        return CourseOffering.objects.filter(
            teacher=self.request.user.teacher_profile,
            semester__is_active=True
        ).select_related('course', 'semester')


@method_decorator(login_required, name='dispatch')
@method_decorator(teacher_required, name='dispatch')
class AttendanceEntryView(View):
    """Attendance entry for a specific course"""
    template_name = 'teacher_portal/attendance/entry.html'
    
    def get(self, request, offering_pk):
        offering = get_object_or_404(CourseOffering, pk=offering_pk)
        enrollments = Enrollment.objects.filter(
            course_offering=offering,
            enroll_status='enrolled'
        ).select_related('student', 'student__user')
        
        return render(request, self.template_name, {
            'offering': offering,
            'enrollments': enrollments,
            'today': timezone.now().date()
        })
    
    def post(self, request, offering_pk):
        from apps.attendance.models import AttendanceRecord
        
        offering = get_object_or_404(CourseOffering, pk=offering_pk)
        attendance_date = request.POST.get('attendance_date')
        
        if not attendance_date:
            messages.error(request, _('Please select an attendance date'))
            return self.get(request, offering_pk)
        
        # Get all enrolled students
        enrollments = Enrollment.objects.filter(
            course_offering=offering,
            enroll_status='enrolled'
        )
        
        saved_count = 0
        for enrollment in enrollments:
            status = request.POST.get(f'status_{enrollment.pk}', 'present')
            remarks = request.POST.get(f'remarks_{enrollment.pk}', '')
            
            # Update or create attendance record
            AttendanceRecord.objects.update_or_create(
                enrollment=enrollment,
                attendance_date=attendance_date,
                defaults={
                    'status': status,
                    'remarks': remarks,
                    'recorded_by': request.user
                }
            )
            saved_count += 1
        
        messages.success(request, _('Attendance saved for %(count)d students on %(date)s') % {
            'count': saved_count,
            'date': attendance_date
        })
        return redirect('teacher_portal:teacher_attendance_entry', offering_pk=offering_pk)


@method_decorator(login_required, name='dispatch')
@method_decorator(teacher_required, name='dispatch')
class BulkAttendanceView(View):
    """Bulk attendance entry"""
    template_name = 'teacher_portal/attendance/bulk.html'
    
    def get(self, request, offering_pk):
        offering = get_object_or_404(CourseOffering, pk=offering_pk)
        return render(request, self.template_name, {'offering': offering})
    
    def post(self, request, offering_pk):
        from apps.attendance.models import AttendanceRecord
        from datetime import datetime, timedelta
        
        offering = get_object_or_404(CourseOffering, pk=offering_pk)
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        default_status = request.POST.get('default_status', 'present')
        
        if not start_date or not end_date:
            messages.error(request, _('Please select both start and end dates'))
            return self.get(request, offering_pk)
        
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, _('Invalid date format'))
            return self.get(request, offering_pk)
        
        if start > end:
            messages.error(request, _('Start date must be before end date'))
            return self.get(request, offering_pk)
        
        enrollments = Enrollment.objects.filter(
            course_offering=offering,
            enroll_status='enrolled'
        )
        
        created_count = 0
        current = start
        while current <= end:
            for enrollment in enrollments:
                AttendanceRecord.objects.get_or_create(
                    enrollment=enrollment,
                    attendance_date=current,
                    defaults={
                        'status': default_status,
                        'recorded_by': request.user
                    }
                )
                created_count += 1
            current += timedelta(days=1)
        
        messages.success(request, _('Created %(count)d attendance records from %(start)s to %(end)s') % {
            'count': created_count,
            'start': start_date,
            'end': end_date
        })
        return redirect('teacher_portal:teacher_attendance')


@method_decorator(login_required, name='dispatch')
@method_decorator(teacher_required, name='dispatch')
class MarksEntryListView(ListView):
    """List courses for marks entry"""
    model = CourseOffering
    template_name = 'teacher_portal/marks/list.html'
    context_object_name = 'course_offerings'
    
    def get_queryset(self):
        return CourseOffering.objects.filter(
            teacher=self.request.user.teacher_profile,
            semester__is_active=True
        ).select_related('course', 'semester')


@method_decorator(login_required, name='dispatch')
@method_decorator(teacher_required, name='dispatch')
class MarksEntryDetailView(DetailView):
    """Marks entry page for a course"""
    model = CourseOffering
    template_name = 'teacher_portal/marks/detail.html'
    pk_url_kwarg = 'offering_pk'
    context_object_name = 'offering'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['components'] = self.object.assessment_components.all()
        context['enrollments'] = Enrollment.objects.filter(
            course_offering=self.object,
            enroll_status='enrolled'
        ).select_related('student', 'student__user')
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(teacher_required, name='dispatch')
class ComponentMarksEntryView(View):
    """Enter marks for a specific component"""
    template_name = 'teacher_portal/marks/component_entry.html'
    
    def get(self, request, offering_pk, component_pk):
        from apps.assessments.models import AssessmentComponent, AssessmentScore
        
        offering = get_object_or_404(CourseOffering, pk=offering_pk)
        component = get_object_or_404(AssessmentComponent, pk=component_pk, course_offering=offering)
        enrollments = Enrollment.objects.filter(
            course_offering=offering,
            enroll_status='enrolled'
        ).select_related('student', 'student__user')
        
        # Load existing scores
        existing_scores = {}
        for score in AssessmentScore.objects.filter(
            assessment_component=component,
            enrollment__in=enrollments
        ).select_related('enrollment'):
            existing_scores[score.enrollment.pk] = score
        
        return render(request, self.template_name, {
            'offering': offering,
            'component': component,
            'enrollments': enrollments,
            'existing_scores': existing_scores
        })
    
    def post(self, request, offering_pk, component_pk):
        from apps.assessments.models import AssessmentComponent, AssessmentScore
        
        offering = get_object_or_404(CourseOffering, pk=offering_pk)
        component = get_object_or_404(AssessmentComponent, pk=component_pk, course_offering=offering)
        action = request.POST.get('action', 'save')
        
        enrollments = Enrollment.objects.filter(
            course_offering=offering,
            enroll_status='enrolled'
        )
        
        saved_count = 0
        updated_enrollments = []  # Track which enrollments were updated
        
        for enrollment in enrollments:
            score_value = request.POST.get(f'score_{enrollment.pk}')
            remarks = request.POST.get(f'remarks_{enrollment.pk}', '')
            
            if score_value:
                try:
                    score = float(score_value)
                    # Validate score against max_score
                    if 0 <= score <= float(component.max_score):
                        AssessmentScore.objects.update_or_create(
                            enrollment=enrollment,
                            assessment_component=component,
                            defaults={
                                'score': score,
                                'remarks': remarks,
                                'status': 'submitted' if action == 'submit' else 'draft',
                                'entered_by': request.user
                            }
                        )
                        saved_count += 1
                        updated_enrollments.append(enrollment)
                except ValueError:
                    continue
        
        # Trigger recalculation for updated enrollments
        if updated_enrollments:
            from .academic_services import (
                AcademicRecalculationService,
                EarlyWarningCalculationService,
                ResultReadinessService
            )
            
            recalc_success = 0
            recalc_failed = 0
            warning_success = 0
            warning_failed = 0
            failed_students = []
            
            for enrollment in updated_enrollments:
                student_name = enrollment.student.user.get_full_name()
                
                # Step 1: Recalculate final result
                try:
                    AcademicRecalculationService.recalculate_enrollment(enrollment)
                    recalc_success += 1
                except Exception as e:
                    recalc_failed += 1
                    failed_students.append(f"{student_name} (result)")
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Failed to recalculate result for {student_name}: {e}")
                    continue
                
                # Step 2: Update early warnings
                try:
                    EarlyWarningCalculationService.update_early_warning(enrollment)
                    warning_success += 1
                except Exception as e:
                    warning_failed += 1
                    if f"{student_name} (result)" not in failed_students:
                        failed_students.append(f"{student_name} (warning)")
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Failed to update warning for {student_name}: {e}")
            
            # Build detailed status message
            if recalc_success > 0:
                messages.success(
                    request, 
                    _('Results calculated for %(count)d students') % {'count': recalc_success}
                )
            
            if warning_success > 0:
                messages.success(
                    request,
                    _('Warning levels updated for %(count)d students') % {'count': warning_success}
                )
            
            if recalc_failed > 0 or warning_failed > 0:
                messages.warning(
                    request,
                    _('Processing incomplete for some students. Check Result Readiness page for details.')
                )
                
                # Add info message showing which students had issues
                if failed_students[:3]:  # Show first 3
                    messages.info(
                        request,
                        _('Issues with: %(students)s') % {
                            'students': ', '.join(failed_students[:3])
                        } + ('...' if len(failed_students) > 3 else '')
                    )
        
        if action == 'submit':
            messages.success(request, _('Marks submitted for %(count)d students') % {'count': saved_count})
        else:
            messages.success(request, _('Marks saved as draft for %(count)d students') % {'count': saved_count})
        
        return redirect('teacher_portal:teacher_marks_entry', offering_pk=offering_pk)


@method_decorator(login_required, name='dispatch')
@method_decorator(teacher_required, name='dispatch')
class GradeSubmissionView(View):
    """Submit grades for a course - triggers GPA calculation"""
    template_name = 'teacher_portal/grades/submit.html'

    def get(self, request, offering_pk):
        offering = get_object_or_404(CourseOffering, pk=offering_pk)
        return render(request, self.template_name, {'offering': offering})

    def post(self, request, offering_pk):
        offering = get_object_or_404(CourseOffering, pk=offering_pk)
        confirm = request.POST.get('confirm')

        if not confirm:
            messages.error(request, _('Please confirm that all grades are correct before submitting'))
            return self.get(request, offering_pk)

        # Update course status
        offering.status = 'grading'
        offering.save(update_fields=['status'])

        # Trigger final result calculation and GPA recalculation for all enrolled students
        enrollments = Enrollment.objects.filter(
            course_offering=offering,
            enroll_status='enrolled'
        ).select_related('student')

        gpa_calculated_count = 0
        for enrollment in enrollments:
            try:
                # Use hardened pipeline to calculate and create FinalResult
                from .academic_services import (
                    FinalResultCalculationService, 
                    GPACalculationService,
                    EarlyWarningCalculationService
                )

                # Step 1: Calculate final result from assessment scores
                final_result = FinalResultCalculationService.calculate_and_create_final_result(enrollment)
                
                # Step 2: Publish the result (now eligible for GPA calculation)
                FinalResultCalculationService.publish_final_result(final_result, request.user)

                # Step 3: Recalculate student's semester GPA/CGPA
                gpa_service = GPACalculationService()
                semester_gpa, credits = gpa_service.calculate_semester_gpa(
                    enrollment.student, 
                    offering.semester
                )
                cgpa, total_credits = gpa_service.calculate_cgpa(enrollment.student)
                
                # Update student record
                enrollment.student.cgpa = cgpa
                enrollment.student.total_credits = total_credits
                enrollment.student.save(update_fields=['cgpa', 'total_credits'])
                
                # Step 4: Update early warnings for the student
                EarlyWarningCalculationService.update_early_warning(enrollment)
                
                gpa_calculated_count += 1
            except ValidationError as e:
                # Log validation error but continue with other students
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Validation error for student {enrollment.student}: {e}")
                continue
            except Exception as e:
                # Log unexpected error but continue
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error processing student {enrollment.student}: {e}")
                continue

        # Create audit log entry
        create_audit_log(
            request,
            action='update',
            module='Grades',
            entity_type='CourseOffering',
            entity_id=offering.pk,
            entity_repr=str(offering),
            description=f'Grades submitted by {request.user.get_full_name()}. GPA calculated for {gpa_calculated_count} students.',
        )

        messages.success(request, _('Grades submitted successfully for %(course)s. GPA calculated for %(count)d students. They are now pending approval.') % {
            'course': offering.course.get_title,
            'count': gpa_calculated_count
        })
        return redirect('teacher_portal:teacher_course_detail', offering_pk=offering_pk)


@method_decorator(login_required, name='dispatch')
@method_decorator(teacher_required, name='dispatch')
class AtRiskStudentListView(ListView):
    """List at-risk students in teacher's courses"""
    template_name = 'teacher_portal/at_risk/list.html'
    context_object_name = 'at_risk_students'
    
    def get_queryset(self):
        teacher = self.request.user.teacher_profile
        return EarlyWarningResult.objects.filter(
            student__enrollments__course_offering__teacher=teacher,
            warning_level__in=['orange', 'red']
        ).select_related('student', 'student__user', 'semester').distinct()


@method_decorator(login_required, name='dispatch')
@method_decorator(teacher_required, name='dispatch')
class StudentInterventionView(View):
    """Add intervention for at-risk student"""
    template_name = 'teacher_portal/at_risk/intervene.html'
    
    def get(self, request, student_pk):
        student = get_object_or_404(Student, pk=student_pk)
        return render(request, self.template_name, {'student': student})
    
    def post(self, request, student_pk):
        from apps.warnings.models import EarlyWarningResult
        from apps.semesters.models import Semester
        
        student = get_object_or_404(Student, pk=student_pk)
        
        intervention_type = request.POST.get('intervention_type')
        intervention_date = request.POST.get('intervention_date')
        description = request.POST.get('description')
        follow_up = request.POST.get('follow_up', '')
        severity = request.POST.get('severity', 'yellow')
        
        if not all([intervention_type, intervention_date, description]):
            messages.error(request, _('Please fill in all required fields'))
            return self.get(request, student_pk)
        
        # Get active semester
        semester = Semester.objects.filter(is_active=True).first()
        if not semester:
            messages.error(request, _('No active semester found'))
            return self.get(request, student_pk)
        
        # Get or create warning result
        result, created = EarlyWarningResult.objects.get_or_create(
            student=student,
            semester=semester,
            defaults={
                'warning_level': severity,
                'risk_score': 30 if severity == 'yellow' else 50 if severity == 'orange' else 70,
                'risk_factors': [],
                'recommendations': []
            }
        )
        
        # Add intervention record to risk factors
        intervention_record = {
            'rule': 'Teacher Intervention',
            'category': 'teacher_intervention',
            'intervention_type': intervention_type,
            'date': intervention_date,
            'description': description,
            'follow_up': follow_up,
            'severity': severity,
            'teacher': request.user.get_full_name()
        }
        
        if isinstance(result.risk_factors, list):
            result.risk_factors.append(intervention_record)
        else:
            result.risk_factors = [intervention_record]
        
        # Update warning level if more severe
        severity_order = {'green': 0, 'yellow': 1, 'orange': 2, 'red': 3}
        if severity_order.get(severity, 0) > severity_order.get(result.warning_level, 0):
            result.warning_level = severity
        
        result.save()
        
        messages.success(request, _('Intervention recorded successfully for %(student)s') % {
            'student': student.user.get_full_name()
        })
        return redirect('teacher_portal:teacher_at_risk')


@method_decorator(login_required, name='dispatch')
@method_decorator(teacher_required, name='dispatch')
class ResultReadinessCheckView(DetailView):
    """Check if course is ready for final result generation"""
    model = CourseOffering
    template_name = 'teacher_portal/results/readiness_check.html'
    pk_url_kwarg = 'offering_pk'
    context_object_name = 'offering'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .academic_services import ResultReadinessService
        
        # Get readiness report for the entire course offering
        readiness_report = ResultReadinessService.check_offering_readiness(self.object)
        context['readiness_report'] = readiness_report
        
        # Get component list for reference
        from apps.assessments.models import AssessmentComponent
        context['components'] = AssessmentComponent.objects.filter(
            course_offering=self.object
        ).order_by('assessment_type', 'name')
        
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(teacher_required, name='dispatch')
class TeacherAnalyticsView(TemplateView):
    """Teacher analytics dashboard"""
    template_name = 'teacher_portal/analytics/dashboard.html'


@method_decorator(login_required, name='dispatch')
@method_decorator(teacher_required, name='dispatch')
class CourseAnalyticsView(DetailView):
    """Analytics for a specific course"""
    model = CourseOffering
    template_name = 'teacher_portal/analytics/course.html'
    pk_url_kwarg = 'offering_pk'
    context_object_name = 'offering'


# ============================================
# Teacher Portal - Assessment Component Management
# ============================================

@method_decorator(login_required, name='dispatch')
@method_decorator(teacher_required, name='dispatch')
class TeacherAssessmentComponentListView(ListView):
    """List assessment components for a teacher's course offering"""
    model = AssessmentComponent
    template_name = 'teacher_portal/assessments/components/list.html'
    context_object_name = 'components'

    def get_queryset(self):
        offering = get_object_or_404(
            CourseOffering,
            pk=self.kwargs['offering_pk'],
            teacher=self.request.user.teacher_profile
        )
        return AssessmentComponent.objects.filter(
            course_offering=offering
        ).order_by('component_type', 'name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['offering'] = get_object_or_404(
            CourseOffering,
            pk=self.kwargs['offering_pk'],
            teacher=self.request.user.teacher_profile
        )
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(teacher_required, name='dispatch')
class TeacherAssessmentComponentCreateView(CreateView):
    """Create assessment component for a teacher's course"""
    model = AssessmentComponent
    template_name = 'teacher_portal/assessments/components/form.html'
    fields = ['name', 'component_type', 'weight_percentage', 'max_score', 'due_date', 'description']

    def dispatch(self, request, *args, **kwargs):
        self.offering = get_object_or_404(
            CourseOffering,
            pk=kwargs['offering_pk'],
            teacher=request.user.teacher_profile
        )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.course_offering = self.offering
        messages.success(self.request, _('Assessment component created successfully'))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['offering'] = self.offering
        context['title'] = _('Create Assessment Component')
        return context

    def get_success_url(self):
        return reverse_lazy('teacher_portal:teacher_assessment_components', kwargs={'offering_pk': self.offering.pk})


@method_decorator(login_required, name='dispatch')
@method_decorator(teacher_required, name='dispatch')
class TeacherAssessmentComponentUpdateView(UpdateView):
    """Edit assessment component for a teacher's course"""
    model = AssessmentComponent
    template_name = 'teacher_portal/assessments/components/form.html'
    pk_url_kwarg = 'component_pk'
    fields = ['name', 'component_type', 'weight_percentage', 'max_score', 'due_date', 'description']

    def dispatch(self, request, *args, **kwargs):
        self.offering = get_object_or_404(
            CourseOffering,
            pk=kwargs['offering_pk'],
            teacher=request.user.teacher_profile
        )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return AssessmentComponent.objects.filter(course_offering=self.offering)

    def form_valid(self, form):
        messages.success(self.request, _('Assessment component updated successfully'))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['offering'] = self.offering
        context['title'] = _('Edit Assessment Component')
        return context

    def get_success_url(self):
        return reverse_lazy('teacher_portal:teacher_assessment_components', kwargs={'offering_pk': self.offering.pk})


@method_decorator(login_required, name='dispatch')
@method_decorator(teacher_required, name='dispatch')
class TeacherAssessmentComponentDeleteView(DeleteView):
    """Delete assessment component"""
    model = AssessmentComponent
    template_name = 'teacher_portal/assessments/components/confirm_delete.html'
    pk_url_kwarg = 'component_pk'

    def dispatch(self, request, *args, **kwargs):
        self.offering = get_object_or_404(
            CourseOffering,
            pk=kwargs['offering_pk'],
            teacher=request.user.teacher_profile
        )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return AssessmentComponent.objects.filter(course_offering=self.offering)

    def delete(self, request, *args, **kwargs):
        messages.success(request, _('Assessment component deleted successfully'))
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('teacher_portal:teacher_assessment_components', kwargs={'offering_pk': self.offering.pk})


# ============================================
# Teacher Portal - Announcement Management
# ============================================

@method_decorator(login_required, name='dispatch')
@method_decorator(teacher_required, name='dispatch')
class TeacherAnnouncementListView(ListView):
    """List announcements created by the teacher"""
    model = Announcement
    template_name = 'teacher_portal/announcements/list.html'
    context_object_name = 'announcements'
    paginate_by = 20

    def get_queryset(self):
        return Announcement.objects.filter(
            published_by=self.request.user
        ).order_by('-created_at')


@method_decorator(login_required, name='dispatch')
@method_decorator(teacher_required, name='dispatch')
class TeacherAnnouncementCreateView(CreateView):
    """Create announcement for teacher's course students"""
    model = Announcement
    template_name = 'teacher_portal/announcements/form.html'
    fields = ['title', 'content', 'target_audience', 'is_active']

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Only allow selecting courses taught by this teacher
        teacher = self.request.user.teacher_profile
        form.fields['target_audience'].queryset = CourseOffering.objects.filter(
            teacher=teacher,
            semester__is_active=True
        ).select_related('course', 'semester')
        return form

    def form_valid(self, form):
        form.instance.published_by = self.request.user
        messages.success(self.request, _('Announcement published successfully'))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Create Announcement')
        return context

    def get_success_url(self):
        return reverse_lazy('teacher_portal:teacher_announcements')


@method_decorator(login_required, name='dispatch')
@method_decorator(teacher_required, name='dispatch')
class TeacherAnnouncementUpdateView(UpdateView):
    """Edit teacher's announcement"""
    model = Announcement
    template_name = 'teacher_portal/announcements/form.html'
    fields = ['title', 'content', 'target_audience', 'is_active']

    def get_queryset(self):
        return Announcement.objects.filter(published_by=self.request.user)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        teacher = self.request.user.teacher_profile
        form.fields['target_audience'].queryset = CourseOffering.objects.filter(
            teacher=teacher
        ).select_related('course', 'semester')
        return form

    def form_valid(self, form):
        messages.success(self.request, _('Announcement updated successfully'))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Edit Announcement')
        return context

    def get_success_url(self):
        return reverse_lazy('teacher_portal:teacher_announcements')


@method_decorator(login_required, name='dispatch')
@method_decorator(teacher_required, name='dispatch')
class TeacherAnnouncementDeleteView(DeleteView):
    """Delete teacher's announcement"""
    model = Announcement
    template_name = 'teacher_portal/announcements/confirm_delete.html'

    def get_queryset(self):
        return Announcement.objects.filter(published_by=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, _('Announcement deleted successfully'))
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('teacher_portal:teacher_announcements')


@method_decorator(login_required, name='dispatch')
@method_decorator(teacher_required, name='dispatch')
class TeacherProfileView(View):
    """Teacher profile management - view and edit profile"""
    template_name = 'teacher_portal/profile.html'
    
    def get(self, request):
        from apps.teachers.models import Teacher
        try:
            teacher = Teacher.objects.get(user=request.user)
        except Teacher.DoesNotExist:
            messages.error(request, _('Teacher profile not found'))
            return redirect('teacher_portal:teacher_dashboard')
        
        return render(request, self.template_name, {
            'teacher': teacher,
        })
    
    def post(self, request):
        from apps.teachers.models import Teacher
        try:
            teacher = Teacher.objects.get(user=request.user)
        except Teacher.DoesNotExist:
            messages.error(request, _('Teacher profile not found'))
            return redirect('teacher_portal:teacher_dashboard')
        
        # Update Teacher model fields
        teacher.specialization = request.POST.get('specialization', teacher.specialization)
        teacher.office_location = request.POST.get('office_location', teacher.office_location)
        teacher.office_hours = request.POST.get('office_hours', teacher.office_hours)
        teacher.bio = request.POST.get('bio', teacher.bio)
        teacher.research_interests = request.POST.get('research_interests', teacher.research_interests)
        teacher.research_abilities = request.POST.get('research_abilities', teacher.research_abilities)
        teacher.publications = request.POST.get('publications', teacher.publications)
        teacher.education_background = request.POST.get('education_background', teacher.education_background)
        teacher.teaching_interests = request.POST.get('teaching_interests', teacher.teaching_interests)
        teacher.professional_experience = request.POST.get('professional_experience', teacher.professional_experience)
        teacher.awards_and_honors = request.POST.get('awards_and_honors', teacher.awards_and_honors)
        teacher.website = request.POST.get('website', teacher.website)
        teacher.linkedin = request.POST.get('linkedin', teacher.linkedin)
        teacher.save()
        
        # Update User model fields
        user = request.user
        user.full_name_en = request.POST.get('full_name_en', user.full_name_en)
        user.full_name_zh = request.POST.get('full_name_zh', user.full_name_zh)
        user.phone = request.POST.get('phone', user.phone)
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']
        user.save()
        
        messages.success(request, _('Profile updated successfully'))
        return redirect('teacher_portal:teacher_profile')


# ============================================
# Student Portal Views
# ============================================

@method_decorator(login_required, name='dispatch')
@method_decorator(student_required, name='dispatch')
class StudentDashboardView(TemplateView):
    """Student dashboard"""
    template_name = 'student_portal/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user.student_profile
        
        # Current semester enrollments
        context['current_enrollments'] = Enrollment.objects.filter(
            student=student,
            course_offering__semester__is_active=True
        ).select_related('course_offering', 'course_offering__course')
        
        # GPA/CGPA info
        context['cgpa'] = student.cgpa
        from apps.results.summary_models import SemesterSummary
        current_summary = SemesterSummary.objects.filter(
            student=student,
            semester__is_active=True
        ).first()
        context['current_gpa'] = current_summary.semester_gpa if current_summary else 0.00
        
        # Current warning status
        warning = EarlyWarningResult.objects.filter(
            student=student,
            semester__is_active=True
        ).first()
        context['warning_level'] = warning.warning_level if warning else 'green'
        
        # Latest announcements
        context['latest_announcements'] = Announcement.objects.filter(
            is_active=True
        ).order_by('-created_at')[:5]
        
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(student_required, name='dispatch')
class StudentCourseListView(ListView):
    """List student's courses"""
    model = Enrollment
    template_name = 'student_portal/courses/list.html'
    context_object_name = 'enrollments'
    
    def get_queryset(self):
        return Enrollment.objects.filter(
            student=self.request.user.student_profile
        ).select_related(
            'course_offering', 
            'course_offering__course',
            'course_offering__semester'
        ).order_by('-course_offering__semester__start_date')


@method_decorator(login_required, name='dispatch')
@method_decorator(student_required, name='dispatch')
class StudentCourseDetailView(DetailView):
    """View course details for student with component scores"""
    model = Enrollment
    template_name = 'student_portal/courses/detail.html'
    pk_url_kwarg = 'enrollment_pk'
    context_object_name = 'enrollment'

    def get_queryset(self):
        # Ensure students can only view their own enrollments
        return Enrollment.objects.filter(
            student=self.request.user.student_profile
        ).select_related(
            'course_offering',
            'course_offering__course',
            'course_offering__semester',
            'course_offering__teacher'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        enrollment = self.object

        # Get assessment components and scores
        from apps.assessments.models import AssessmentComponent, AssessmentScore
        components = AssessmentComponent.objects.filter(
            course_offering=enrollment.course_offering
        )

        # Build component scores list
        component_scores = []
        for component in components:
            score = AssessmentScore.objects.filter(
                enrollment=enrollment,
                assessment_component=component
            ).first()
            component_scores.append({
                'component': component,
                'score': score
            })

        context['component_scores'] = component_scores
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(student_required, name='dispatch')
class StudentResultsView(ListView):
    """View all results"""
    model = Enrollment
    template_name = 'student_portal/results/list.html'
    context_object_name = 'enrollments'
    
    def get_queryset(self):
        return Enrollment.objects.filter(
            student=self.request.user.student_profile,
            final_result__is_published=True
        ).select_related(
            'course_offering',
            'course_offering__course',
            'course_offering__semester',
            'final_result'
        ).order_by('-course_offering__semester__start_date')


@method_decorator(login_required, name='dispatch')
@method_decorator(student_required, name='dispatch')
class SemesterResultsView(ListView):
    """View results for a specific semester"""
    model = Enrollment
    template_name = 'student_portal/results/semester.html'
    context_object_name = 'enrollments'
    
    def get_queryset(self):
        return Enrollment.objects.filter(
            student=self.request.user.student_profile,
            course_offering__semester_id=self.kwargs['semester_pk'],
            final_result__is_published=True
        ).select_related('course_offering', 'course_offering__course', 'final_result')


@method_decorator(login_required, name='dispatch')
@method_decorator(student_required, name='dispatch')
class StudentGPAView(TemplateView):
    """View GPA/CGPA details"""
    template_name = 'student_portal/gpa/view.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user.student_profile
        
        context['cgpa'] = student.cgpa
        context['total_credits'] = student.total_credits_earned
        
        from apps.results.summary_models import SemesterSummary
        context['semester_summaries'] = SemesterSummary.objects.filter(
            student=student
        ).select_related('semester').order_by('-semester__academic_year', 'semester__semester_type')
        
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(student_required, name='dispatch')
class StudentAttendanceView(ListView):
    """View attendance summary"""
    model = Enrollment
    template_name = 'student_portal/attendance/list.html'
    context_object_name = 'enrollments'
    
    def get_queryset(self):
        return Enrollment.objects.filter(
            student=self.request.user.student_profile,
            course_offering__semester__is_active=True
        ).select_related('course_offering', 'course_offering__course')


@method_decorator(login_required, name='dispatch')
@method_decorator(student_required, name='dispatch')
class CourseAttendanceView(DetailView):
    """View attendance for a specific course"""
    model = Enrollment
    template_name = 'student_portal/attendance/course.html'
    pk_url_kwarg = 'enrollment_pk'
    context_object_name = 'enrollment'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attendance_records'] = self.object.attendance_records.all().order_by('-attendance_date')
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(student_required, name='dispatch')
class StudentWarningsView(ListView):
    """View warning history"""
    model = EarlyWarningResult
    template_name = 'student_portal/warnings/list.html'
    context_object_name = 'warnings'
    
    def get_queryset(self):
        return EarlyWarningResult.objects.filter(
            student=self.request.user.student_profile
        ).select_related('semester').order_by('-generated_at')


@method_decorator(login_required, name='dispatch')
@method_decorator(student_required, name='dispatch')
class AcknowledgeWarningView(View):
    """Acknowledge a warning"""
    
    def post(self, request, pk):
        warning = get_object_or_404(
            EarlyWarningResult, 
            pk=pk, 
            student=request.user.student_profile
        )
        warning.is_acknowledged = True
        warning.acknowledged_at = timezone.now()
        warning.save()
        messages.success(request, _('Warning acknowledged'))
        return redirect('student_portal:student_warnings')


@method_decorator(login_required, name='dispatch')
@method_decorator(student_required, name='dispatch')
class StudentTranscriptView(TemplateView):
    """View transcript with semester grouping and GPA calculation"""
    template_name = 'student_portal/transcript/view.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user.student_profile
        
        context['student'] = student
        
        # Get published enrollments with results
        enrollments = Enrollment.objects.filter(
            student=student,
            final_result__is_published=True
        ).select_related(
            'course_offering__course',
            'course_offering__semester',
            'final_result'
        ).order_by('course_offering__semester__start_date')
        
        # Group by semester with repeated course handling
        from collections import defaultdict
        semester_data = defaultdict(lambda: {'courses': [], 'total_credits': 0, 'total_points': Decimal('0')})
        course_best_grades = {}
        
        for enrollment in enrollments:
            semester = enrollment.course_offering.semester
            course = enrollment.course_offering.course
            result = enrollment.final_result
            
            if not result:
                continue
            
            grade_point = float(enrollment.final_result.grade_point) if enrollment.final_result.grade_point is not None else 0.0 or Decimal('0')
            credits = course.credit_hours
            
            # Track best grade for repeated courses
            course_key = (semester.id, course.id)
            if course_key not in course_best_grades or grade_point > course_best_grades[course_key]['grade_point']:
                course_best_grades[course_key] = {
                    'enrollment': enrollment,
                    'grade_point': grade_point,
                    'credits': credits
                }
        
        # Build semester data with best grades only
        for course_key, data in course_best_grades.items():
            semester = data['enrollment'].course_offering.semester
            semester_data[semester]['courses'].append(data['enrollment'])
            semester_data[semester]['total_credits'] += data['credits']
            semester_data[semester]['total_points'] += data['grade_point'] * data['credits']
        
        # Calculate semester GPAs
        transcript_data = []
        cumulative_points = Decimal('0')
        cumulative_credits = Decimal('0')
        
        for semester in sorted(semester_data.keys(), key=lambda s: s.start_date):
            data = semester_data[semester]
            if data['total_credits'] > 0:
                gpa = (data['total_points'] / data['total_credits']).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            else:
                gpa = Decimal('0.00')
            
            cumulative_points += data['total_points']
            cumulative_credits += data['total_credits']
            
            if cumulative_credits > 0:
                cgpa = (cumulative_points / cumulative_credits).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            else:
                cgpa = Decimal('0.00')
            
            transcript_data.append({
                'semester': semester,
                'courses': data['courses'],
                'semester_gpa': gpa,
                'semester_credits': data['total_credits'],
                'cgpa': cgpa,
                'cumulative_credits': cumulative_credits
            })
        
        context['transcript_data'] = transcript_data
        context['final_cgpa'] = cgpa if transcript_data else Decimal('0.00')
        context['total_credits'] = cumulative_credits
        
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(student_required, name='dispatch')
class DownloadTranscriptView(View):
    """Download transcript as PDF or Excel"""
    
    def get(self, request):
        student = request.user.student_profile
        format_type = request.GET.get('format', 'pdf')
        
        if format_type == 'excel':
            # Generate Excel
            from apps.core.report_services import ReportGenerator
            return ReportGenerator.generate_transcript_excel(student)
        else:
            # Generate PDF
            from apps.core.report_services import TranscriptPDFGenerator
            generator = TranscriptPDFGenerator(student)
            pdf_buffer = generator.generate()
            
            if pdf_buffer is None:
                messages.error(request, _('Error generating transcript. Please try again.'))
                return redirect('student_portal:student_transcript')
            
            # Create response
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="transcript_{student.student_no}.pdf"'
            response.write(pdf_buffer.getvalue())
            pdf_buffer.close()
            
            return response


@method_decorator(login_required, name='dispatch')
@method_decorator(student_required, name='dispatch')
class StudentAnnouncementListView(ListView):
    """View announcements for student"""
    model = Announcement
    template_name = 'student_portal/announcements/list.html'
    context_object_name = 'announcements'
    paginate_by = 20
    
    def get_queryset(self):
        student = self.request.user.student_profile
        # Get announcements that are either:
        # 1. General announcements (no target audience)
        # 2. Targeted at courses the student is enrolled in
        from django.db.models import Q
        
        enrolled_course_ids = Enrollment.objects.filter(
            student=student
        ).values_list('course_offering_id', flat=True)
        
        return Announcement.objects.filter(
            Q(is_active=True),
            Q(target_audience__isnull=True) | Q(target_audience_id__in=enrolled_course_ids)
        ).select_related('target_audience', 'target_audience__course', 'published_by').order_by('-created_at')


@method_decorator(login_required, name='dispatch')
@method_decorator(student_required, name='dispatch')
class StudentProfileView(TemplateView):
    """Student profile and settings view"""
    template_name = 'student_portal/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['student'] = self.request.user.student_profile
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle profile updates"""
        user = request.user
        student = user.student_profile
        
        # Update user info
        user.full_name_en = request.POST.get('full_name_en', user.full_name_en)
        user.full_name_zh = request.POST.get('full_name_zh', user.full_name_zh)
        user.phone = request.POST.get('phone', user.phone)
        user.save()
        
        # Update student info (only allowed fields)
        student.guardian_name = request.POST.get('guardian_name', student.guardian_name)
        student.guardian_phone = request.POST.get('guardian_phone', student.guardian_phone)
        student.guardian_email = request.POST.get('guardian_email', student.guardian_email)
        student.save()
        
        messages.success(request, _('Profile updated successfully'))
        return redirect('student_portal:student_profile')


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class EnrollmentDeleteView(DeleteView):
    """Delete an enrollment"""
    model = Enrollment
    template_name = 'admin_portal/enrollments/delete.html'
    success_url = reverse_lazy('admin_portal:admin_enrollments')
    
    def get_object(self):
        return get_object_or_404(Enrollment, pk=self.kwargs['pk'])
    
    def delete(self, request, *args, **kwargs):
        enrollment = self.get_object()
        student_name = enrollment.student.user.get_full_name()
        course_name = enrollment.course_offering.course.title_en
        
        messages.success(
            request, 
            _('Successfully removed %(student)s from %(course)s') % {
                'student': student_name,
                'course': course_name
            }
        )
        return super().delete(request, *args, **kwargs)
