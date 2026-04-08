#!/usr/bin/env python
"""
Production Data Seeder
1. Clears all demo/seed data
2. Inserts real production data with ALL fields populated
"""

import os
import django
import random
from datetime import datetime, date, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.db import transaction
from django.contrib.auth import get_user_model
from apps.departments.models import Department
from apps.programs.models import Program
from apps.semesters.models import Semester
from apps.courses.models import Course
from apps.accounts.models import Role
from apps.students.models import Student
from apps.teachers.models import Teacher
from apps.enrollments.models import Enrollment
from apps.assessments.models import AssessmentComponent
from apps.warnings.models import EarlyWarningRule

User = get_user_model()


def clear_all_demo_data():
    """Clear all demo/seed data but keep system tables"""
    print("Clearing demo data...")
    
    # Clear in reverse order to avoid FK constraints
    from apps.warnings.models import EarlyWarningResult, EarlyWarningRule
    from apps.warnings.extended_models import WarningIntervention, WarningHistory, WarningEvidence, WarningEscalationRule, WarningResolution
    from apps.results.models import FinalResult, GradeScheme, GradeMapping
    from apps.attendance.models import AttendanceRecord
    from apps.assessments.models import AssessmentScore
    from apps.notifications.models import Notification
    from apps.auditlogs.models import AuditLog
    
    EarlyWarningResult.objects.all().delete()
    EarlyWarningRule.objects.all().delete()
    WarningIntervention.objects.all().delete()
    WarningHistory.objects.all().delete()
    WarningEvidence.objects.all().delete()
    WarningEscalationRule.objects.all().delete()
    WarningResolution.objects.all().delete()
    FinalResult.objects.all().delete()
    GradeMapping.objects.all().delete()
    GradeScheme.objects.all().delete()
    AssessmentScore.objects.all().delete()
    AttendanceRecord.objects.all().delete()
    Enrollment.objects.all().delete()
    AssessmentComponent.objects.all().delete()
    
    # Clear course offerings (has FK to Teacher)
    from apps.courses.offering_models import CourseOffering
    CourseOffering.objects.all().delete()
    
    # Clear students and teachers first (before users)
    Student.objects.all().delete()
    Teacher.objects.all().delete()
    
    # Clear users except superuser
    User.objects.filter(is_superuser=False).delete()
    
    # Clear courses and reference data
    Course.objects.all().delete()
    Program.objects.all().delete()
    Semester.objects.all().delete()
    Department.objects.all().delete()
    
    # Clear audit logs and notifications
    AuditLog.objects.all().delete()
    Notification.objects.all().delete()
    
    print("Demo data cleared!")


def seed_departments():
    """Seed real university departments"""
    print("Seeding departments...")
    
    departments = [
        {
            'name_en': 'Computer Science',
            'name_zh': '计算机科学系',
            'code': 'CS',
            'description_en': 'Department of Computer Science and Engineering',
            'description_zh': '计算机科学与工程系',
            'status': 'active'
        },
        {
            'name_en': 'Electrical Engineering',
            'name_zh': '电气工程系',
            'code': 'EE',
            'description_en': 'Department of Electrical Engineering',
            'description_zh': '电气工程系',
            'status': 'active'
        },
        {
            'name_en': 'Business Administration',
            'name_zh': '工商管理系',
            'code': 'BA',
            'description_en': 'Department of Business Administration',
            'description_zh': '工商管理系',
            'status': 'active'
        },
        {
            'name_en': 'Mathematics',
            'name_zh': '数学系',
            'code': 'MATH',
            'description_en': 'Department of Mathematics',
            'description_zh': '数学系',
            'status': 'active'
        },
        {
            'name_en': 'Physics',
            'name_zh': '物理系',
            'code': 'PHY',
            'description_en': 'Department of Physics',
            'description_zh': '物理系',
            'status': 'active'
        }
    ]
    
    dept_objects = []
    for dept_data in departments:
        dept = Department.objects.create(**dept_data)
        dept_objects.append(dept)
    
    print(f"Created {len(dept_objects)} departments")
    return dept_objects


def seed_programs(departments):
    """Seed academic programs"""
    print("Seeding programs...")
    
    programs = [
        {
            'name_en': 'Bachelor of Computer Science',
            'name_zh': '计算机科学学士',
            'code': 'BCS',
            'degree_level': 'bachelor',
            'department': departments[0],
            'description_en': 'Four-year undergraduate program in Computer Science',
            'description_zh': '计算机科学四年制本科课程',
            'status': 'active'
        },
        {
            'name_en': 'Bachelor of Electrical Engineering',
            'name_zh': '电气工程学士',
            'code': 'BEE',
            'degree_level': 'bachelor',
            'department': departments[1],
            'description_en': 'Four-year undergraduate program in Electrical Engineering',
            'description_zh': '电气工程四年制本科课程',
            'status': 'active'
        },
        {
            'name_en': 'MBA Program',
            'name_zh': '工商管理硕士',
            'code': 'MBA',
            'degree_level': 'master',
            'department': departments[2],
            'description_en': 'Master of Business Administration',
            'description_zh': '工商管理硕士课程',
            'status': 'active'
        }
    ]
    
    prog_objects = []
    for prog_data in programs:
        prog = Program.objects.create(**prog_data)
        prog_objects.append(prog)
    
    print(f"Created {len(prog_objects)} programs")
    return prog_objects


def seed_semesters():
    """Seed academic semesters"""
    print("Seeding semesters...")
    
    semesters = [
        {
            'academic_year': '2024-2025',
            'semester_type': 'fall',
            'name_en': 'Fall Semester 2024',
            'name_zh': '2024年秋季学期',
            'start_date': date(2024, 9, 1),
            'end_date': date(2025, 1, 15),
            'registration_start': date(2024, 8, 15),
            'registration_end': date(2024, 8, 31),
            'status': 'active',
            'is_active': True
        },
        {
            'academic_year': '2024-2025',
            'semester_type': 'spring',
            'name_en': 'Spring Semester 2025',
            'name_zh': '2025年春季学期',
            'start_date': date(2025, 1, 20),
            'end_date': date(2025, 6, 15),
            'registration_start': date(2025, 1, 5),
            'registration_end': date(2025, 1, 19),
            'status': 'active'
        }
    ]
    
    sem_objects = []
    for sem_data in semesters:
        sem = Semester.objects.create(**sem_data)
        sem_objects.append(sem)
    
    print(f"Created {len(sem_objects)} semesters")
    return sem_objects


def seed_courses(departments, programs):
    """Seed real courses"""
    print("Seeding courses...")
    
    courses = [
        {
            'code': 'CS101',
            'title_en': 'Introduction to Programming',
            'title_zh': '程序设计导论',
            'department': departments[0],
            'credit_hours': 3,
            'description_en': 'Fundamental concepts of programming using Python',
            'description_zh': '使用Python编程的基本概念',
            'status': 'active'
        },
        {
            'code': 'CS201',
            'title_en': 'Data Structures and Algorithms',
            'title_zh': '数据结构与算法',
            'department': departments[0],
            'credit_hours': 4,
            'description_en': 'Advanced data structures and algorithm analysis',
            'description_zh': '高级数据结构与算法分析',
            'status': 'active'
        },
        {
            'code': 'EE101',
            'title_en': 'Circuit Analysis',
            'title_zh': '电路分析',
            'department': departments[1],
            'credit_hours': 3,
            'description_en': 'Fundamentals of electrical circuit analysis',
            'description_zh': '电路分析基础',
            'status': 'active'
        },
        {
            'code': 'MATH101',
            'title_en': 'Calculus I',
            'title_zh': '微积分 I',
            'department': departments[3],
            'credit_hours': 4,
            'description_en': 'Differential and integral calculus',
            'description_zh': '微分与积分微积分',
            'status': 'active'
        },
        {
            'code': 'PHY101',
            'title_en': 'General Physics I',
            'title_zh': '普通物理 I',
            'department': departments[4],
            'credit_hours': 3,
            'description_en': 'Mechanics and thermodynamics',
            'description_zh': '力学与热力学',
            'status': 'active'
        },
        {
            'code': 'BA101',
            'title_en': 'Principles of Management',
            'title_zh': '管理学原理',
            'department': departments[2],
            'credit_hours': 3,
            'description_en': 'Introduction to management principles',
            'description_zh': '管理学原理导论',
            'status': 'active'
        }
    ]
    
    course_objects = []
    for course_data in courses:
        course = Course.objects.create(**course_data)
        course_objects.append(course)
    
    print(f"Created {len(course_objects)} courses")
    return course_objects


def seed_users_teachers(departments):
    """Seed teacher users"""
    print("Seeding teachers...")
    
    teacher_role = Role.objects.get(code='teacher')
    
    teachers_data = [
        {
            'email': 'zhang.prof@university.edu',
            'full_name_en': 'Prof. Zhang Wei',
            'full_name_zh': '张伟教授',
            'specialization': 'Artificial Intelligence',
            'department': departments[0],
            'office_location': 'Building A, Room 301',
            'office_hours': 'Mon/Wed 2:00-4:00 PM',
            'bio_en': 'Ph.D. in Computer Science with 15 years teaching experience',
            'bio_zh': '计算机科学博士，拥有15年教学经验'
        },
        {
            'email': 'li.prof@university.edu',
            'full_name_en': 'Prof. Li Ming',
            'full_name_zh': '李明教授',
            'specialization': 'Power Systems',
            'department': departments[1],
            'office_location': 'Building B, Room 205',
            'office_hours': 'Tue/Thu 10:00-12:00 PM',
            'bio_en': 'Expert in electrical power systems and renewable energy',
            'bio_zh': '电力系统与可再生能源专家'
        },
        {
            'email': 'wang.prof@university.edu',
            'full_name_en': 'Prof. Wang Fang',
            'full_name_zh': '王芳教授',
            'specialization': 'Business Strategy',
            'department': departments[2],
            'office_location': 'Building C, Room 102',
            'office_hours': 'Mon/Fri 1:00-3:00 PM',
            'bio_en': 'MBA with expertise in strategic management',
            'bio_zh': 'MBA，战略管理专家'
        }
    ]
    
    teacher_objects = []
    for idx, t_data in enumerate(teachers_data):
        dept = t_data.pop('department')
        
        user = User.objects.create(
            email=t_data['email'],
            full_name_en=t_data['full_name_en'],
            full_name_zh=t_data['full_name_zh'],
            is_active=True,
            role=teacher_role
        )
        user.set_password('Teacher123!')
        user.save()
        
        teacher = Teacher.objects.create(
            user=user,
            teacher_no=f'T{idx+1:04d}',
            department=dept,
            specialization=t_data['specialization'],
            office_location=t_data['office_location'],
            office_hours=t_data['office_hours'],
            bio=t_data['bio_en'],
            join_date=date(2015, 9, 1),
            status='active'
        )
        teacher_objects.append(teacher)
    
    print(f"Created {len(teacher_objects)} teachers")
    return teacher_objects


def seed_users_students(programs, semesters):
    """Seed student users"""
    print("Seeding students...")
    
    student_role = Role.objects.get(code='student')
    first_semester = semesters[0] if semesters else None
    
    # Generate 20 students
    students_data = []
    for i in range(1, 21):
        students_data.append({
            'email': f'student{i:03d}@university.edu',
            'full_name_en': f'Student {i:03d}',
            'full_name_zh': f'学生{i:03d}',
            'student_no': f'2024{i:04d}',
            'program': random.choice(programs),
            'batch_year': '2024',
            'current_semester': first_semester,
            'status': 'active'
        })
    
    student_objects = []
    for s_data in students_data:
        program = s_data.pop('program')
        
        user = User.objects.create(
            email=s_data['email'],
            full_name_en=s_data['full_name_en'],
            full_name_zh=s_data['full_name_zh'],
            is_active=True,
            phone=f'138{i:04d}{i:04d}'[:11],
            role=student_role
        )
        user.set_password('Student123!')
        user.save()
        
        student = Student.objects.create(
            user=user,
            student_no=s_data['student_no'],
            program=program,
            department=program.department,
            batch_year=s_data['batch_year'],
            current_semester=s_data['current_semester'],
            status=s_data['status']
        )
        student_objects.append(student)
    
    print(f"Created {len(student_objects)} students")
    return student_objects


def seed_course_offerings(courses, teachers, semesters):
    """Seed course offerings"""
    print("Seeding course offerings...")
    
    from apps.courses.offering_models import CourseOffering
    
    offerings = []
    for i, course in enumerate(courses):
        teacher = teachers[i % len(teachers)]
        semester = semesters[0]  # Fall semester
        
        offering = CourseOffering.objects.create(
            course=course,
            teacher=teacher,
            semester=semester,
            section_name=f'Section {chr(65 + (i % 3))}',  # A, B, C
            room=f'Room {201 + i}',
            day_of_week='mon,wed',
            start_time='09:00',
            end_time='10:30',
            capacity=40,
            status='active'
        )
        offerings.append(offering)
    
    print(f"Created {len(offerings)} course offerings")
    return offerings


def seed_enrollments(students, offerings):
    """Seed student enrollments"""
    print("Seeding enrollments...")
    
    enrollments = []
    for student in students:
        # Each student enrolls in 3-4 random courses
        selected_offerings = random.sample(offerings, random.randint(3, 4))
        
        for offering in selected_offerings:
            enrollment = Enrollment.objects.create(
                student=student,
                course_offering=offering,
                enroll_status='enrolled',
                enrolled_at=datetime.now()
            )
            enrollments.append(enrollment)
            
            # Update enrolled count
            offering.enrolled_count += 1
            offering.save()
    
    print(f"Created {len(enrollments)} enrollments")
    return enrollments


def seed_assessment_components(offerings):
    """Seed assessment components for each course"""
    print("Seeding assessment components...")
    
    components = []
    for offering in offerings:
        # Standard components
        comp_data = [
            {
                'course_offering': offering,
                'name': 'Attendance',
                'assessment_type': 'attendance',
                'weight_percentage': 10.00,
                'max_score': 100.00,
                'description': 'Class attendance and participation',
                'order': 1
            },
            {
                'course_offering': offering,
                'name': 'Assignments',
                'assessment_type': 'assignment',
                'weight_percentage': 20.00,
                'max_score': 100.00,
                'description': 'Weekly assignments',
                'order': 2
            },
            {
                'course_offering': offering,
                'name': 'Midterm Exam',
                'assessment_type': 'midterm',
                'weight_percentage': 30.00,
                'max_score': 100.00,
                'description': 'Midterm examination',
                'order': 3
            },
            {
                'course_offering': offering,
                'name': 'Final Exam',
                'assessment_type': 'final',
                'weight_percentage': 40.00,
                'max_score': 100.00,
                'description': 'Final examination',
                'order': 4
            }
        ]
        
        for comp in comp_data:
            component = AssessmentComponent.objects.create(**comp)
            components.append(component)
    
    print(f"Created {len(components)} assessment components")
    return components


def seed_early_warning_rules():
    """Seed early warning rules"""
    print("Seeding early warning rules...")
    
    rules = [
        {
            'code': 'LOW_ATTENDANCE',
            'name': 'Low Attendance Alert',
            'description': 'Student attendance below 70%',
            'category': 'attendance',
            'threshold_value': 70,
            'comparison_operator': '<',
            'weight': 30,
            'severity': 'yellow',
            'is_active': True,
            'order': 1
        },
        {
            'code': 'LOW_GRADE',
            'name': 'Low Grade Alert',
            'description': 'Student average below 60%',
            'category': 'grade',
            'threshold_value': 60,
            'comparison_operator': '<',
            'weight': 40,
            'severity': 'red',
            'is_active': True,
            'order': 2
        },
        {
            'code': 'MISSING_ASSIGNMENTS',
            'name': 'Missing Assignments',
            'description': 'More than 2 missing assignments',
            'category': 'assignment',
            'threshold_value': 2,
            'comparison_operator': '>',
            'weight': 30,
            'severity': 'yellow',
            'is_active': True,
            'order': 3
        }
    ]
    
    rule_objects = []
    for rule_data in rules:
        rule = EarlyWarningRule.objects.create(**rule_data)
        rule_objects.append(rule)
    
    print(f"Created {len(rule_objects)} early warning rules")
    return rule_objects


def create_admin_user():
    """Create admin user if not exists"""
    print("Checking admin user...")
    
    if not User.objects.filter(email='admin@university.edu').exists():
        admin_role = Role.objects.get(code='admin')
        
        admin = User.objects.create_superuser(
            email='admin@university.edu',
            password='Admin123!',
            full_name_en='System Administrator',
            full_name_zh='系统管理员',
            is_active=True,
            is_email_verified=True
        )
        admin.roles.add(admin_role)
        admin.save()
        print("Created admin user: admin@university.edu / Admin123!")
    else:
        print("Admin user already exists")


def run_production_seeder():
    """Main function to reset and seed production data"""
    print("="*60)
    print("PRODUCTION DATA SEEDER")
    print("="*60)
    
    with transaction.atomic():
        # Step 1: Clear demo data
        clear_all_demo_data()
        
        # Step 2: Ensure admin exists
        create_admin_user()
        
        # Step 3: Seed reference data
        departments = seed_departments()
        programs = seed_programs(departments)
        semesters = seed_semesters()
        courses = seed_courses(departments, programs)
        
        # Step 4: Seed users
        teachers = seed_users_teachers(departments)
        students = seed_users_students(programs, semesters)
        
        # Step 5: Seed academic data
        offerings = seed_course_offerings(courses, teachers, semesters)
        enrollments = seed_enrollments(students, offerings)
        components = seed_assessment_components(offerings)
        rules = seed_early_warning_rules()
    
    print("="*60)
    print("PRODUCTION DATA SEEDED SUCCESSFULLY!")
    print("="*60)
    print("\nDefault credentials:")
    print("  Admin: admin@university.edu / Admin123!")
    print("  Teachers: zhang.prof@university.edu / Teacher123!")
    print("  Students: student001@university.edu / Student123!")
    print("="*60)


if __name__ == '__main__':
    run_production_seeder()
