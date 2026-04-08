"""
Tests for enrollments app
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.accounts.models import Role
from apps.departments.models import Department
from apps.programs.models import Program
from apps.semesters.models import Semester
from apps.courses.models import Course
from apps.courses.offering_models import CourseOffering
from apps.teachers.models import Teacher
from apps.students.models import Student
from apps.enrollments.models import Enrollment

User = get_user_model()


class EnrollmentModelTests(TestCase):
    """Test Enrollment model"""
    
    def setUp(self):
        # Setup dependencies
        self.department = Department.objects.create(code='CS', name_en='CS')
        self.program = Program.objects.create(
            code='CS-BS', name_en='CS BS', department=self.department, degree_level='bachelor', duration_years=4
        )
        self.semester = Semester.objects.create(
            academic_year='2023-2024', semester_type='fall', name_en='Fall 2023', name_zh='2023秋季'
        )
        self.course = Course.objects.create(
            code='CS101', title_en='Programming', credit_hours=3, department=self.department
        )
        
        teacher_role = Role.objects.create(name='Teacher', code='teacher')
        teacher_user = User.objects.create_user(email='teacher@test.com', full_name_en='Teacher', password='pass', role=teacher_role)
        self.teacher = Teacher.objects.create(user=teacher_user, teacher_no='T001', department=self.department)
        
        student_role = Role.objects.create(name='Student', code='student')
        student_user = User.objects.create_user(email='student@test.com', full_name_en='Student', password='pass', role=student_role)
        self.student = Student.objects.create(
            user=student_user, student_no='S001', department=self.department, program=self.program,
            current_semester=self.semester, batch_year=2023
        )
        
        self.offering = CourseOffering.objects.create(
            course=self.course, semester=self.semester, teacher=self.teacher, section_name='A', capacity=30
        )
        
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            course_offering=self.offering,
            enroll_status='enrolled'
        )
    
    def test_enrollment_creation(self):
        """Test enrollment can be created"""
        self.assertEqual(self.enrollment.student.student_no, 'S001')
        self.assertEqual(self.enrollment.course_offering.course.code, 'CS101')
        self.assertEqual(self.enrollment.enroll_status, 'enrolled')
        self.assertEqual(self.enrollment.attendance_percentage, 0.0)
    
    def test_enrollment_str(self):
        """Test enrollment string representation"""
        expected = 'S001 - CS101 (Fall 2023)'
        self.assertEqual(str(self.enrollment), expected)
