from django.urls import path
from . import views

app_name = 'student_portal'

urlpatterns = [
    # Dashboard
    path('', views.StudentDashboardView.as_view(), name='student_dashboard'),
    
    # Courses
    path('courses/', views.StudentCourseListView.as_view(), name='student_courses'),
    path('course/<int:enrollment_pk>/', views.StudentCourseDetailView.as_view(), name='student_course_detail_alt'),
    path('courses/<int:enrollment_pk>/', views.StudentCourseDetailView.as_view(), name='student_course_detail'),
    
    # Results
    path('results/', views.StudentResultsView.as_view(), name='student_results'),
    path('results/semester/<int:semester_pk>/', views.SemesterResultsView.as_view(), name='student_semester_results'),
    
    # GPA/CGPA
    path('gpa/', views.StudentGPAView.as_view(), name='student_gpa'),
    
    # Attendance
    path('attendance/', views.StudentAttendanceView.as_view(), name='student_attendance'),
    path('attendance/course/<int:enrollment_pk>/', views.CourseAttendanceView.as_view(), name='student_course_attendance'),
    
    # Warnings
    path('warnings/', views.StudentWarningsView.as_view(), name='student_warnings'),
    path('warnings/<int:pk>/acknowledge/', views.AcknowledgeWarningView.as_view(), name='student_acknowledge_warning'),
    
    # Transcript
    path('transcript/', views.StudentTranscriptView.as_view(), name='student_transcript'),
    path('transcript/download/', views.DownloadTranscriptView.as_view(), name='student_download_transcript'),
    
    # Announcements
    path('announcements/', views.StudentAnnouncementListView.as_view(), name='student_announcements'),
    
    # Profile
    path('profile/', views.StudentProfileView.as_view(), name='student_profile'),
]
