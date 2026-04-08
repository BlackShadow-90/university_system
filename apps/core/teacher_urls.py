from django.urls import path
from . import views

app_name = 'teacher_portal'

urlpatterns = [
    # Dashboard
    path('', views.TeacherDashboardView.as_view(), name='teacher_dashboard'),
    
    # Courses
    path('courses/', views.TeacherCourseListView.as_view(), name='teacher_courses'),
    path('courses/<int:offering_pk>/', views.TeacherCourseDetailView.as_view(), name='teacher_course_detail'),
    path('courses/<int:offering_pk>/students/', views.CourseStudentListView.as_view(), name='teacher_course_students'),

    # Assessment Components (Teacher Management)
    path('courses/<int:offering_pk>/assessments/', views.TeacherAssessmentComponentListView.as_view(), name='teacher_assessment_components'),
    path('courses/<int:offering_pk>/assessments/create/', views.TeacherAssessmentComponentCreateView.as_view(), name='teacher_assessment_component_create'),
    path('courses/<int:offering_pk>/assessments/<int:component_pk>/edit/', views.TeacherAssessmentComponentUpdateView.as_view(), name='teacher_assessment_component_edit'),
    path('courses/<int:offering_pk>/assessments/<int:component_pk>/delete/', views.TeacherAssessmentComponentDeleteView.as_view(), name='teacher_assessment_component_delete'),

    # Attendance
    path('attendance/', views.TeacherAttendanceView.as_view(), name='teacher_attendance'),
    path('attendance/course/<int:offering_pk>/', views.AttendanceEntryView.as_view(), name='teacher_attendance_entry'),
    path('attendance/course/<int:offering_pk>/bulk/', views.BulkAttendanceView.as_view(), name='teacher_attendance_bulk'),

    # Marks Entry
    path('marks/', views.MarksEntryListView.as_view(), name='teacher_marks'),
    path('marks/course/<int:offering_pk>/', views.MarksEntryDetailView.as_view(), name='teacher_marks_entry'),
    path('marks/course/<int:offering_pk>/component/<int:component_pk>/', views.ComponentMarksEntryView.as_view(), name='teacher_component_marks'),

    # Grade Submission
    path('grades/course/<int:offering_pk>/submit/', views.GradeSubmissionView.as_view(), name='teacher_grade_submit'),
    
    # Result Readiness Check
    path('grades/course/<int:offering_pk>/readiness/', views.ResultReadinessCheckView.as_view(), name='teacher_result_readiness'),

    # At-Risk Students
    path('at-risk/', views.AtRiskStudentListView.as_view(), name='teacher_at_risk'),
    path('at-risk/<int:student_pk>/intervene/', views.StudentInterventionView.as_view(), name='teacher_intervention'),

    # Analytics
    path('analytics/', views.TeacherAnalyticsView.as_view(), name='teacher_analytics'),
    path('analytics/course/<int:offering_pk>/', views.CourseAnalyticsView.as_view(), name='teacher_course_analytics'),

    # Announcements (Teacher)
    path('announcements/', views.TeacherAnnouncementListView.as_view(), name='teacher_announcements'),
    path('announcements/create/', views.TeacherAnnouncementCreateView.as_view(), name='teacher_announcement_create'),
    path('announcements/<int:pk>/edit/', views.TeacherAnnouncementUpdateView.as_view(), name='teacher_announcement_edit'),
    path('announcements/<int:pk>/delete/', views.TeacherAnnouncementDeleteView.as_view(), name='teacher_announcement_delete'),
    
    # Teacher Profile
    path('profile/', views.TeacherProfileView.as_view(), name='teacher_profile'),
]
