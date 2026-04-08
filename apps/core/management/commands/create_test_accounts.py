"""
Management command to create sample test accounts for development
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.accounts.models import User, Role
from apps.departments.models import Department
from apps.programs.models import Program
from apps.semesters.models import Semester
from apps.teachers.models import Teacher
from apps.students.models import Student


class Command(BaseCommand):
    help = 'Create sample test accounts for teachers and students'

    def handle(self, *args, **options):
        self.stdout.write('Creating test accounts...')
        
        with transaction.atomic():
            # Get or create roles
            teacher_role, _ = Role.objects.get_or_create(
                code='teacher',
                defaults={'name': 'Teacher', 'description': 'Teacher Role'}
            )
            student_role, _ = Role.objects.get_or_create(
                code='student',
                defaults={'name': 'Student', 'description': 'Student Role'}
            )
            
            # Get or create department
            dept, _ = Department.objects.get_or_create(
                code='CS',
                defaults={
                    'name_en': 'Computer Science',
                    'name_zh': '计算机科学'
                }
            )
            
            # Get or create program
            program, _ = Program.objects.get_or_create(
                code='CS-BS',
                defaults={
                    'name_en': 'Computer Science BS',
                    'name_zh': '计算机科学学士',
                    'department': dept,
                    'degree_level': 'bachelor',
                    'duration_years': 4
                }
            )
            
            # Get or create semester
            semester, _ = Semester.objects.get_or_create(
                academic_year='2023-2024',
                semester_type='fall',
                defaults={
                    'name_en': 'Fall 2023',
                    'name_zh': '2023秋季',
                    'is_active': True
                }
            )
            
            # Create test teacher
            teacher_user, created = User.objects.get_or_create(
                email='teacher@test.com',
                defaults={
                    'full_name_en': 'John Smith',
                    'full_name_zh': '约翰·史密斯',
                    'role': teacher_role,
                    'status': 'active',
                    'is_staff': False
                }
            )
            if created:
                teacher_user.set_password('teacher123')
                teacher_user.save()
                Teacher.objects.create(
                    user=teacher_user,
                    teacher_no='TCH001',
                    department=dept,
                    title='associate_professor',
                    specialization='Artificial Intelligence',
                    join_date='2020-09-01'
                )
                self.stdout.write(self.style.SUCCESS(f'Created teacher: {teacher_user.email} / password: teacher123'))
            else:
                self.stdout.write(f'Teacher already exists: {teacher_user.email}')
            
            # Create test student
            student_user, created = User.objects.get_or_create(
                email='student@test.com',
                defaults={
                    'full_name_en': 'Alice Johnson',
                    'full_name_zh': '爱丽丝·约翰逊',
                    'role': student_role,
                    'status': 'active',
                    'is_staff': False
                }
            )
            if created:
                student_user.set_password('student123')
                student_user.save()
                Student.objects.create(
                    user=student_user,
                    student_no='STU001',
                    department=dept,
                    program=program,
                    current_semester=semester,
                    batch_year=2023,
                    gender='female',
                    date_of_birth='2000-05-15'
                )
                self.stdout.write(self.style.SUCCESS(f'Created student: {student_user.email} / password: student123'))
            else:
                self.stdout.write(f'Student already exists: {student_user.email}')
        
        self.stdout.write(self.style.SUCCESS('Test accounts created successfully!'))
        self.stdout.write('')
        self.stdout.write('Login credentials:')
        self.stdout.write('  Teacher: teacher@test.com / teacher123')
        self.stdout.write('  Student: student@test.com / student123')
