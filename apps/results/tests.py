"""
Tests for results app
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
from apps.results.models import FinalResult, GradeScheme, GradeMapping
from apps.results.summary_models import SemesterSummary, CGPARecord

User = get_user_model()


class FinalResultModelTests(TestCase):
    """Test FinalResult model"""
    
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
        
        self.enrollment = Enrollment.objects.create(student=self.student, course_offering=self.offering)
        
        self.result = FinalResult.objects.create(
            enrollment=self.enrollment,
            total_score=85.5,
            letter_grade='A',
            grade_point=4.0,
            pass_fail_status='pass',
            quality_points=12.0
        )
    
    def test_result_creation(self):
        """Test final result can be created"""
        self.assertEqual(self.result.total_score, 85.5)
        self.assertEqual(self.result.letter_grade, 'A')
        self.assertEqual(self.result.grade_point, 4.0)
        self.assertEqual(self.result.pass_fail_status, 'pass')
        self.assertFalse(self.result.is_published)
    
    def test_result_str(self):
        """Test result string representation"""
        expected = 'S001 - CS101: A (Pass)'
        self.assertEqual(str(self.result), expected)


class GradeSchemeModelTests(TestCase):
    """Test GradeScheme and GradeMapping models"""
    
    def setUp(self):
        self.scheme = GradeScheme.objects.create(
            name='Standard 4.0',
            is_default=True,
            description='Standard 4.0 GPA scale'
        )
        
        self.mapping_a = GradeMapping.objects.create(
            scheme=self.scheme,
            letter_grade='A',
            grade_point=4.0,
            min_percentage=90,
            max_percentage=100,
            is_passing=True,
            order=1
        )
    
    def test_scheme_creation(self):
        """Test grade scheme can be created"""
        self.assertEqual(self.scheme.name, 'Standard 4.0')
        self.assertTrue(self.scheme.is_default)
    
    def test_mapping_creation(self):
        """Test grade mapping can be created"""
        self.assertEqual(self.mapping_a.letter_grade, 'A')
        self.assertEqual(self.mapping_a.grade_point, 4.0)
        self.assertTrue(self.mapping_a.is_passing)
