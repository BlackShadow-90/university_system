"""
Tests for students app
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.accounts.models import Role
from apps.departments.models import Department
from apps.programs.models import Program
from apps.students.models import Student
from apps.semesters.models import Semester

User = get_user_model()


class StudentModelTests(TestCase):
    """Test Student model"""
    
    def setUp(self):
        self.role = Role.objects.create(name='Student', code='student')
        self.department = Department.objects.create(
            code='CS',
            name_en='Computer Science',
            name_zh='计算机科学'
        )
        self.program = Program.objects.create(
            code='CS-BS',
            name_en='Computer Science BS',
            name_zh='计算机科学学士',
            department=self.department,
            degree_level='bachelor',
            duration_years=4
        )
        self.semester = Semester.objects.create(
            academic_year='2023-2024',
            semester_type='fall',
            name_en='Fall 2023',
            name_zh='2023秋季'
        )
        self.user = User.objects.create_user(
            email='student@test.com',
            full_name_en='Test Student',
            password='testpass123',
            role=self.role
        )
        self.student = Student.objects.create(
            user=self.user,
            student_no='STU2023001',
            department=self.department,
            program=self.program,
            current_semester=self.semester,
            batch_year=2023,
            gender='male',
            date_of_birth='2000-01-01'
        )
    
    def test_student_creation(self):
        """Test student can be created"""
        self.assertEqual(self.student.student_no, 'STU2023001')
        self.assertEqual(self.student.user.get_full_name(), 'Test Student')
        self.assertEqual(self.student.department.code, 'CS')
        self.assertEqual(self.student.program.code, 'CS-BS')
        self.assertEqual(self.student.cgpa, 0.00)
    
    def test_student_str(self):
        """Test student string representation"""
        self.assertEqual(str(self.student), 'STU2023001 - Test Student')
