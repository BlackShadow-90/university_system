from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Report generation endpoints
    path('transcript/<int:student_id>/', views.GenerateTranscriptView.as_view(), name='generate_transcript'),
    path('semester-report/<int:student_id>/<int:semester_id>/', views.GenerateSemesterReportView.as_view(), name='generate_semester_report'),
    path('course-report/<int:offering_id>/', views.GenerateCourseReportView.as_view(), name='generate_course_report'),
    path('warning-report/', views.GenerateWarningReportView.as_view(), name='generate_warning_report'),
    path('attendance-report/<int:offering_id>/', views.GenerateAttendanceReportView.as_view(), name='generate_attendance_report'),
    
    # Export endpoints
    path('export/students/', views.ExportStudentsView.as_view(), name='export_students'),
    path('export/grades/', views.ExportGradesView.as_view(), name='export_grades'),
    path('export/enrollments/', views.ExportEnrollmentsView.as_view(), name='export_enrollments'),
]
