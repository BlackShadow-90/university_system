from django.urls import path
from . import views

app_name = 'admin_portal'

urlpatterns = [
    # Dashboard
    path('', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    
    # User Management
    path('users/', views.UserListView.as_view(), name='admin_users'),
    path('users/create/', views.UserCreateView.as_view(), name='admin_user_create'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='admin_user_detail'),
    path('users/<int:pk>/edit/', views.UserUpdateView.as_view(), name='admin_user_edit'),
    path('users/<int:pk>/delete/', views.UserDeleteView.as_view(), name='admin_user_delete'),
    
    # Student Management
    path('students/', views.StudentListView.as_view(), name='admin_students'),
    path('students/create/', views.StudentCreateView.as_view(), name='admin_student_create'),
    path('students/<int:pk>/', views.StudentDetailView.as_view(), name='admin_student_detail'),
    path('students/<int:pk>/edit/', views.StudentUpdateView.as_view(), name='admin_student_edit'),
    path('students/<int:pk>/delete/', views.StudentDeleteView.as_view(), name='admin_student_delete'),
    path('students/import/', views.StudentImportView.as_view(), name='admin_student_import'),
    
    # Teacher Management
    path('teachers/', views.TeacherListView.as_view(), name='admin_teachers'),
    path('teachers/create/', views.TeacherCreateView.as_view(), name='admin_teacher_create'),
    path('teachers/<int:pk>/', views.TeacherDetailView.as_view(), name='admin_teacher_detail'),
    path('teachers/<int:pk>/edit/', views.TeacherUpdateView.as_view(), name='admin_teacher_edit'),
    path('teachers/<int:pk>/delete/', views.TeacherDeleteView.as_view(), name='admin_teacher_delete'),
    
    # Department Management
    path('departments/', views.DepartmentListView.as_view(), name='admin_departments'),
    path('departments/create/', views.DepartmentCreateView.as_view(), name='admin_department_create'),
    path('departments/<int:pk>/edit/', views.DepartmentUpdateView.as_view(), name='admin_department_edit'),
    path('departments/<int:pk>/delete/', views.DepartmentDeleteView.as_view(), name='admin_department_delete'),
    
    # Program Management
    path('programs/', views.ProgramListView.as_view(), name='admin_programs'),
    path('programs/create/', views.ProgramCreateView.as_view(), name='admin_program_create'),
    path('programs/<int:pk>/edit/', views.ProgramUpdateView.as_view(), name='admin_program_edit'),
    
    # Semester Management
    path('semesters/', views.SemesterListView.as_view(), name='admin_semesters'),
    path('semesters/create/', views.SemesterCreateView.as_view(), name='admin_semester_create'),
    path('semesters/<int:pk>/edit/', views.SemesterUpdateView.as_view(), name='admin_semester_edit'),
    
    # Course Management
    path('courses/', views.CourseListView.as_view(), name='admin_courses'),
    path('courses/create/', views.CourseCreateView.as_view(), name='admin_course_create'),
    path('courses/<int:pk>/edit/', views.CourseUpdateView.as_view(), name='admin_course_edit'),
    
    # Course Offerings
    path('offerings/', views.CourseOfferingListView.as_view(), name='admin_offerings'),
    path('offerings/create/', views.CourseOfferingCreateView.as_view(), name='admin_offering_create'),
    path('offerings/<int:pk>/edit/', views.CourseOfferingUpdateView.as_view(), name='admin_offering_edit'),
    path('offerings/<int:pk>/delete/', views.CourseOfferingDeleteView.as_view(), name='admin_offering_delete'),
    path('offerings/<int:pk>/components/', views.OfferingComponentListView.as_view(), name='admin_offering_components'),
    path('offerings/<int:pk>/components/add/', views.OfferingComponentCreateView.as_view(), name='admin_offering_component_add'),
    path('offerings/<int:offering_pk>/components/<int:component_pk>/edit/', views.OfferingComponentUpdateView.as_view(), name='admin_offering_component_edit'),
    path('offerings/<int:offering_pk>/components/<int:component_pk>/delete/', views.OfferingComponentDeleteView.as_view(), name='admin_offering_component_delete'),
    
    # Enrollment Management
    path('enrollments/', views.EnrollmentListView.as_view(), name='admin_enrollments'),
    path('enrollments/bulk/', views.BulkEnrollmentView.as_view(), name='admin_bulk_enrollment'),
    path('enrollments/<int:pk>/delete/', views.EnrollmentDeleteView.as_view(), name='admin_enrollment_delete'),
    
    # Warnings
    path('warnings/', views.WarningListView.as_view(), name='admin_warnings'),
    path('warnings/rules/', views.WarningRuleListView.as_view(), name='admin_warning_rules'),
    path('warnings/calculate/', views.CalculateWarningsView.as_view(), name='admin_calculate_warnings'),
    path('warnings/manual/', views.ManualWarningCreateView.as_view(), name='admin_manual_warning'),
    path('warnings/<int:pk>/clear/', views.ClearWarningView.as_view(), name='admin_clear_warning'),
    
    # Announcements
    path('announcements/', views.AnnouncementListView.as_view(), name='admin_announcements'),
    path('announcements/create/', views.AnnouncementCreateView.as_view(), name='admin_announcement_create'),
    path('announcements/<int:pk>/edit/', views.AnnouncementUpdateView.as_view(), name='admin_announcement_edit'),
    path('announcements/<int:pk>/delete/', views.AnnouncementDeleteView.as_view(), name='admin_announcement_delete'),
    
    # Reports
    path('reports/', views.ReportsView.as_view(), name='admin_reports'),
    path('reports/students/', views.StudentReportView.as_view(), name='admin_student_report'),
    path('reports/grades/', views.GradeReportView.as_view(), name='admin_grade_report'),
    path('reports/warnings/', views.WarningReportView.as_view(), name='admin_warning_report'),
    
    # Settings
    path('settings/', views.SettingsView.as_view(), name='admin_settings'),
    path('settings/grade-policy/', views.GradePolicyView.as_view(), name='admin_grade_policy'),
    
    # Audit Logs
    path('audit-logs/', views.AuditLogListView.as_view(), name='admin_audit_logs'),
]
