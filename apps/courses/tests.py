"""
Tests for courses app
"""
from django.test import TestCase
from apps.departments.models import Department
from apps.courses.models import Course


class CourseModelTests(TestCase):
    """Test Course model"""
    
    def setUp(self):
        self.department = Department.objects.create(
            code='CS',
            name_en='Computer Science',
            name_zh='计算机科学'
        )
        self.course = Course.objects.create(
            code='CS101',
            title_en='Introduction to Programming',
            title_zh='程序设计导论',
            credit_hours=3,
            lecture_hours=3,
            lab_hours=1,
            course_type='core',
            department=self.department,
            description_en='Basic programming concepts',
            description_zh='基础编程概念'
        )
    
    def test_course_creation(self):
        """Test course can be created"""
        self.assertEqual(self.course.code, 'CS101')
        self.assertEqual(self.course.title_en, 'Introduction to Programming')
        self.assertEqual(self.course.credit_hours, 3)
        self.assertEqual(self.course.department.code, 'CS')
        self.assertEqual(self.course.course_type, 'core')
    
    def test_course_str(self):
        """Test course string representation"""
        self.assertEqual(str(self.course), 'CS101 - Introduction to Programming')
