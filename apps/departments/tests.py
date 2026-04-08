"""
Tests for departments app
"""
from django.test import TestCase
from apps.departments.models import Department


class DepartmentModelTests(TestCase):
    """Test Department model"""
    
    def setUp(self):
        self.department = Department.objects.create(
            code='CS',
            name_en='Computer Science',
            name_zh='计算机科学',
            description_en='Computer Science Department',
            description_zh='计算机科学系'
        )
    
    def test_department_creation(self):
        """Test department can be created"""
        self.assertEqual(self.department.code, 'CS')
        self.assertEqual(self.department.name_en, 'Computer Science')
        self.assertEqual(self.department.name_zh, '计算机科学')
        self.assertEqual(self.department.status, 'active')
    
    def test_department_str(self):
        """Test department string representation"""
        self.assertEqual(str(self.department), 'CS - Computer Science')
