"""
Tests for assessments app
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.accounts.models import Role
from apps.departments.models import Department
from apps.programs.models import Program
from apps.courses.models import Course
from apps.courses.offering_models import CourseOffering
from apps.teachers.models import Teacher
from apps.semesters.models import Semester
from apps.assessments.models import AssessmentComponent, AssessmentScore
from apps.students.models import Student
from apps.enrollments.models import Enrollment

User = get_user_model()


class AssessmentComponentModelTests(TestCase):
    """Test AssessmentComponent model"""
    
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
        
        self.offering = CourseOffering.objects.create(
            course=self.course, semester=self.semester, teacher=self.teacher, section_name='A', capacity=30
        )
        
        self.component = AssessmentComponent.objects.create(
            course_offering=self.offering,
            name='Midterm Exam',
            assessment_type='exam',
            weight_percentage=30,
            max_score=100
        )
    
    def test_component_creation(self):
        """Test assessment component can be created"""
        self.assertEqual(self.component.name, 'Midterm Exam')
        self.assertEqual(self.component.assessment_type, 'exam')
        self.assertEqual(self.component.weight_percentage, 30)
        self.assertEqual(self.component.max_score, 100)
    
    def test_component_str(self):
        """Test component string representation"""
        self.assertEqual(str(self.component), 'Midterm Exam (30%)')


class AssessmentScoreModelTests(TestCase):
    """Test AssessmentScore model"""
    
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
        
        self.component = AssessmentComponent.objects.create(
            course_offering=self.offering, name='Midterm', assessment_type='exam', weight_percentage=30, max_score=100
        )
        
        self.score = AssessmentScore.objects.create(
            enrollment=self.enrollment,
            assessment_component=self.component,
            score=85,
            percentage=85.0,
            entered_by=teacher_user
        )
    
    def test_score_creation(self):
        """Test assessment score can be created"""
        self.assertEqual(self.score.score, 85)
        self.assertEqual(self.score.percentage, 85.0)
        self.assertEqual(self.score.status, 'entered')
    
    def test_score_calculations(self):
        """Test score percentage calculation"""
        self.assertEqual(self.score.percentage, 85.0)
