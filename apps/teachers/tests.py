"""
Tests for teachers app
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.accounts.models import Role
from apps.departments.models import Department
from apps.teachers.models import Teacher

User = get_user_model()


class TeacherModelTests(TestCase):
    """Test Teacher model"""
    
    def setUp(self):
        self.role = Role.objects.create(name='Teacher', code='teacher')
        self.department = Department.objects.create(
            code='CS',
            name_en='Computer Science',
            name_zh='计算机科学'
        )
        self.user = User.objects.create_user(
            email='teacher@test.com',
            full_name_en='Test Teacher',
            password='testpass123',
            role=self.role
        )
        self.teacher = Teacher.objects.create(
            user=self.user,
            teacher_no='TCH2023001',
            department=self.department,
            title='associate_professor',
            specialization='Artificial Intelligence',
            join_date='2020-09-01'
        )
    
    def test_teacher_creation(self):
        """Test teacher can be created"""
        self.assertEqual(self.teacher.teacher_no, 'TCH2023001')
        self.assertEqual(self.teacher.user.get_full_name(), 'Test Teacher')
        self.assertEqual(self.teacher.department.code, 'CS')
        self.assertEqual(self.teacher.title, 'associate_professor')
        self.assertEqual(self.teacher.specialization, 'Artificial Intelligence')
    
    def test_teacher_str(self):
        """Test teacher string representation"""
        self.assertEqual(str(self.teacher), 'TCH2023001 - Test Teacher')
