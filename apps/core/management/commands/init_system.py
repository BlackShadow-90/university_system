"""
Management command to initialize system with default data
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.translation import gettext as _

from apps.accounts.models import User, Role
from apps.departments.models import Department
from apps.programs.models import Program
from apps.semesters.models import Semester
from apps.courses.models import Course
from apps.settings_app.models import GradePolicy
from apps.warnings.models import EarlyWarningRule


class Command(BaseCommand):
    help = 'Initialize the system with default roles, permissions, and sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--demo-data',
            action='store_true',
            help='Create demo users and sample data'
        )
        parser.add_argument(
            '--skip-users',
            action='store_true',
            help='Skip creating default users'
        )

    def handle(self, *args, **options):
        demo_data = options.get('demo_data')
        skip_users = options.get('skip_users')
        
        self.stdout.write("Starting system initialization...")
        
        try:
            with transaction.atomic():
                # Create roles
                self._create_roles()
                
                # Create default warning rules
                self._create_default_warning_rules()
                
                # Create demo data if requested
                if demo_data:
                    self._create_demo_departments()
                    self._create_demo_programs()
                    self._create_demo_semesters()
                    
                    if not skip_users:
                        self._create_demo_users()
                        self._create_demo_courses()
                        self._create_demo_offerings()
                        self._create_demo_enrollments()
                        self._create_demo_grades()
                        self._create_demo_attendance()
                        self._create_demo_warnings()
                        self._create_demo_announcements()
                
            self.stdout.write(self.style.SUCCESS("System initialization completed successfully!"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error during initialization: {str(e)}"))
            raise
    
    def _create_roles(self):
        """Create default system roles"""
        self.stdout.write("Creating default roles...")
        
        roles = [
            {'code': 'admin', 'name': 'Administrator', 
             'description': 'System administrator with full access'},
            {'code': 'teacher', 'name': 'Teacher',
             'description': 'Teaching staff with course management access'},
            {'code': 'student', 'name': 'Student',
             'description': 'Student with access to personal academic information'},
            {'code': 'staff', 'name': 'Staff',
             'description': 'Administrative staff with limited system access'},
        ]
        
        for role_data in roles:
            role, created = Role.objects.get_or_create(
                code=role_data['code'],
                defaults=role_data
            )
            if created:
                self.stdout.write(f"  Created role: {role.name}")
            else:
                self.stdout.write(f"  Role already exists: {role.name}")
    
    def _create_default_warning_rules(self):
        """Create default early warning rules"""
        self.stdout.write("Creating default warning rules...")
        
        rules = [
            {
                'code': 'CRIT_ATTEND',
                'name': 'Critical Attendance Warning',
                'category': 'attendance',
                'threshold_value': 70.0,
                'severity': 'red',
                'is_active': True,
                'order': 1,
            },
            {
                'code': 'ATTEND_WARN',
                'name': 'Attendance Warning',
                'category': 'attendance',
                'threshold_value': 80.0,
                'severity': 'orange',
                'is_active': True,
                'order': 2,
            },
            {
                'code': 'LOW_GRADE',
                'name': 'Low Grade Warning',
                'category': 'gpa',
                'threshold_value': 60.0,
                'severity': 'orange',
                'is_active': True,
                'order': 3,
            },
            {
                'code': 'FAIL_GRADE',
                'name': 'Failing Grade Warning',
                'category': 'gpa',
                'threshold_value': 50.0,
                'severity': 'red',
                'is_active': True,
                'order': 4,
            },
        ]
        
        for rule_data in rules:
            rule, created = EarlyWarningRule.objects.get_or_create(
                code=rule_data['code'],
                defaults=rule_data
            )
            if created:
                self.stdout.write(f"  Created warning rule: {rule.name}")
            else:
                self.stdout.write(f"  Warning rule exists: {rule.name}")
    
    def _create_demo_departments(self):
        """Create demo departments"""
        self.stdout.write("Creating demo departments...")
        
        departments = [
            {'code': 'CS', 'name_en': 'Computer Science', 'name_zh': '计算机科学系'},
            {'code': 'ENG', 'name_en': 'Engineering', 'name_zh': '工程系'},
            {'code': 'BUS', 'name_en': 'Business', 'name_zh': '商学院'},
            {'code': 'SCI', 'name_en': 'Science', 'name_zh': '理学系'},
            {'code': 'ART', 'name_en': 'Arts', 'name_zh': '人文学院'},
        ]
        
        for dept_data in departments:
            dept, created = Department.objects.get_or_create(
                code=dept_data['code'],
                defaults=dept_data
            )
            if created:
                self.stdout.write(f"  Created department: {dept.name_en}")
    
    def _create_demo_programs(self):
        """Create demo programs"""
        self.stdout.write("Creating demo programs...")
        
        cs_dept = Department.objects.get(code='CS')
        eng_dept = Department.objects.get(code='ENG')
        bus_dept = Department.objects.get(code='BUS')
        
        programs = [
            {'code': 'CS-BS', 'name_en': 'Bachelor of Computer Science', 'name_zh': '计算机科学学士', 
             'department': cs_dept, 'degree_level': 'bachelor', 'duration_years': 4, 'total_credits': 120},
            {'code': 'SE-BS', 'name_en': 'Bachelor of Software Engineering', 'name_zh': '软件工程学士',
             'department': cs_dept, 'degree_level': 'bachelor', 'duration_years': 4, 'total_credits': 120},
            {'code': 'CE-BS', 'name_en': 'Bachelor of Computer Engineering', 'name_zh': '计算机工程学士',
             'department': eng_dept, 'degree_level': 'bachelor', 'duration_years': 4, 'total_credits': 128},
            {'code': 'MBA', 'name_en': 'Master of Business Administration', 'name_zh': '工商管理硕士',
             'department': bus_dept, 'degree_level': 'master', 'duration_years': 2, 'total_credits': 36},
        ]
        
        for prog_data in programs:
            dept = prog_data.pop('department')
            prog, created = Program.objects.get_or_create(
                code=prog_data['code'],
                defaults={**prog_data, 'department': dept}
            )
            if created:
                self.stdout.write(f"  Created program: {prog.name_en}")
                
                # Grade mappings will be created via settings app
                # when grade policy is configured
    
    def _create_demo_semesters(self):
        """Create demo semesters"""
        self.stdout.write("Creating demo semesters...")
        
        from datetime import date
        
        semesters = [
            {
                'academic_year': '2024-2025',
                'semester_type': 'fall',
                'name_en': 'Fall 2024',
                'name_zh': '2024秋季学期',
                'start_date': date(2024, 9, 1),
                'end_date': date(2024, 12, 20),
                'is_active': True,
            },
            {
                'academic_year': '2024-2025',
                'semester_type': 'spring',
                'name_en': 'Spring 2025',
                'name_zh': '2025春季学期',
                'start_date': date(2025, 1, 15),
                'end_date': date(2025, 5, 15),
                'is_active': False,
            },
        ]
        
        for sem_data in semesters:
            sem, created = Semester.objects.get_or_create(
                academic_year=sem_data['academic_year'],
                semester_type=sem_data['semester_type'],
                defaults=sem_data
            )
            if created:
                self.stdout.write(f"  Created semester: {sem.name_en}")
    
    def _create_demo_users(self):
        """Create demo users: 1 admin, 7 teachers, 7 students"""
        self.stdout.write("Creating demo users...")
        
        # Create admin user
        admin_role = Role.objects.get(code='admin')
        admin_user, created = User.objects.get_or_create(
            email='admin@university.edu',
            defaults={
                'full_name_en': 'System Administrator',
                'full_name_zh': '系统管理员',
                'is_staff': True,
                'is_superuser': True,
                'role': admin_role,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("  Created admin user: admin@university.edu / admin123"))
        
        # Create 7 teachers
        teacher_role = Role.objects.get(code='teacher')
        cs_dept = Department.objects.get(code='CS')
        eng_dept = Department.objects.get(code='ENG')
        bus_dept = Department.objects.get(code='BUS')
        
        teachers_data = [
            {'email': 'teacher1@university.edu', 'name_en': 'John Smith', 'name_zh': '约翰·史密斯', 'dept': cs_dept, 'no': 'T001'},
            {'email': 'teacher2@university.edu', 'name_en': 'Sarah Johnson', 'name_zh': '莎拉·约翰逊', 'dept': cs_dept, 'no': 'T002'},
            {'email': 'teacher3@university.edu', 'name_en': 'Michael Chen', 'name_zh': '迈克尔·陈', 'dept': eng_dept, 'no': 'T003'},
            {'email': 'teacher4@university.edu', 'name_en': 'Emily Davis', 'name_zh': '艾米丽·戴维斯', 'dept': eng_dept, 'no': 'T004'},
            {'email': 'teacher5@university.edu', 'name_en': 'Robert Wilson', 'name_zh': '罗伯特·威尔逊', 'dept': bus_dept, 'no': 'T005'},
            {'email': 'teacher6@university.edu', 'name_en': 'Lisa Brown', 'name_zh': '丽莎·布朗', 'dept': cs_dept, 'no': 'T006'},
            {'email': 'teacher7@university.edu', 'name_en': 'David Lee', 'name_zh': '大卫·李', 'dept': eng_dept, 'no': 'T007'},
        ]
        
        from apps.teachers.models import Teacher
        from datetime import date
        for t_data in teachers_data:
            user, created = User.objects.get_or_create(
                email=t_data['email'],
                defaults={
                    'full_name_en': t_data['name_en'],
                    'full_name_zh': t_data['name_zh'],
                    'is_staff': True,
                    'role': teacher_role,
                }
            )
            if created:
                user.set_password('teacher123')
                user.save()
                Teacher.objects.get_or_create(
                    user=user,
                    defaults={
                        'teacher_no': t_data['no'],
                        'department': t_data['dept'],
                        'specialization': 'General',
                        'join_date': date(2020, 1, 1),
                    }
                )
                self.stdout.write(self.style.SUCCESS(f"  Created teacher: {t_data['name_en']} ({t_data['email']})"))
        
        # Create 7 students
        student_role = Role.objects.get(code='student')
        cs_prog = Program.objects.get(code='CS-BS')
        se_prog = Program.objects.get(code='SE-BS')
        
        students_data = [
            {'email': 'student1@university.edu', 'name_en': 'Alice Wang', 'name_zh': '爱丽丝·王', 'no': 'S001', 'prog': cs_prog, 'dept': cs_dept, 'batch': 2024},
            {'email': 'student2@university.edu', 'name_en': 'Bob Zhang', 'name_zh': '鲍勃·张', 'no': 'S002', 'prog': cs_prog, 'dept': cs_dept, 'batch': 2024},
            {'email': 'student3@university.edu', 'name_en': 'Carol Liu', 'name_zh': '卡罗尔·刘', 'no': 'S003', 'prog': se_prog, 'dept': cs_dept, 'batch': 2024},
            {'email': 'student4@university.edu', 'name_en': 'David Kim', 'name_zh': '大卫·金', 'no': 'S004', 'prog': cs_prog, 'dept': cs_dept, 'batch': 2023},
            {'email': 'student5@university.edu', 'name_en': 'Eva Martinez', 'name_zh': '伊娃·马丁内斯', 'no': 'S005', 'prog': se_prog, 'dept': cs_dept, 'batch': 2023},
            {'email': 'student6@university.edu', 'name_en': 'Frank Huang', 'name_zh': '弗兰克·黄', 'no': 'S006', 'prog': cs_prog, 'dept': cs_dept, 'batch': 2022},
            {'email': 'student7@university.edu', 'name_en': 'Grace Chen', 'name_zh': '格蕾丝·陈', 'no': 'S007', 'prog': se_prog, 'dept': cs_dept, 'batch': 2022},
        ]
        
        from apps.students.models import Student
        for s_data in students_data:
            user, created = User.objects.get_or_create(
                email=s_data['email'],
                defaults={
                    'full_name_en': s_data['name_en'],
                    'full_name_zh': s_data['name_zh'],
                    'role': student_role,
                }
            )
            if created:
                user.set_password('student123')
                user.save()
                Student.objects.get_or_create(
                    user=user,
                    defaults={
                        'student_no': s_data['no'],
                        'program': s_data['prog'],
                        'department': s_data['dept'],
                        'batch_year': s_data['batch'],
                        'status': 'active',
                        'cgpa': 3.5,
                    }
                )
                self.stdout.write(self.style.SUCCESS(f"  Created student: {s_data['name_en']} ({s_data['email']})"))
    
    def _create_demo_courses(self):
        """Create demo courses"""
        self.stdout.write("Creating demo courses...")
        
        cs_dept = Department.objects.get(code='CS')
        
        courses = [
            {'code': 'CS101', 'title_en': 'Introduction to Computer Science', 'title_zh': '计算机科学导论',
             'credit_hours': 3, 'department': cs_dept},
            {'code': 'CS201', 'title_en': 'Data Structures', 'title_zh': '数据结构',
             'credit_hours': 3, 'department': cs_dept},
            {'code': 'CS301', 'title_en': 'Algorithms', 'title_zh': '算法',
             'credit_hours': 3, 'department': cs_dept},
            {'code': 'CS401', 'title_en': 'Database Systems', 'title_zh': '数据库系统',
             'credit_hours': 3, 'department': cs_dept},
        ]
        
        for course_data in courses:
            dept = course_data.pop('department')
            course, created = Course.objects.get_or_create(
                code=course_data['code'],
                defaults={**course_data, 'department': dept}
            )
            if created:
                self.stdout.write(f"  Created course: {course.title_en}")
    
    def _create_demo_offerings(self):
        """Create 7 course offerings"""
        self.stdout.write("Creating demo course offerings...")
        from apps.courses.offering_models import CourseOffering
        from apps.teachers.models import Teacher
        from apps.semesters.models import Semester
        
        semester = Semester.objects.get(academic_year='2024-2025', semester_type='fall')
        courses = Course.objects.filter(code__in=['CS101', 'CS201', 'CS301', 'CS401'])[:4]
        teachers = list(Teacher.objects.all()[:7])
        
        for i, course in enumerate(courses):
            teacher = teachers[i % len(teachers)]
            offering, created = CourseOffering.objects.get_or_create(
                course=course,
                semester=semester,
                defaults={
                    'teacher': teacher,
                    'status': 'open',
                    'capacity': 30,
                }
            )
            if created:
                self.stdout.write(f"  Created offering: {course.code} - {teacher.user.get_full_name()}")
        
        # Create 3 more offerings for spring
        spring = Semester.objects.get(academic_year='2024-2025', semester_type='spring')
        for i, course in enumerate(courses[:3]):
            teacher = teachers[(i + 2) % len(teachers)]
            offering, created = CourseOffering.objects.get_or_create(
                course=course,
                semester=spring,
                defaults={
                    'teacher': teacher,
                    'status': 'open',
                    'capacity': 30,
                }
            )
            if created:
                self.stdout.write(f"  Created spring offering: {course.code}")
    
    def _create_demo_enrollments(self):
        """Create 5-7 enrollments per course"""
        self.stdout.write("Creating demo enrollments...")
        from apps.enrollments.models import Enrollment
        from apps.courses.offering_models import CourseOffering
        from apps.students.models import Student
        
        offerings = CourseOffering.objects.filter(status='open')
        students = list(Student.objects.filter(status='active')[:7])
        
        for offering in offerings:
            # Enroll 5-7 students per offering
            for student in students[:6]:  # 6 students per course
                enrollment, created = Enrollment.objects.get_or_create(
                    student=student,
                    course_offering=offering,
                    defaults={
                        'enroll_status': 'enrolled',
                    }
                )
                if created:
                    self.stdout.write(f"  Enrolled {student.student_no} in {offering.course.code}")
    
    def _create_demo_grades(self):
        """Create 5-7 grade records"""
        self.stdout.write("Creating demo grade records...")
        from apps.results.models import FinalResult
        from apps.enrollments.models import Enrollment
        
        enrollments = Enrollment.objects.filter(enroll_status='enrolled')[:7]
        
        for enrollment in enrollments:
            # Random grades between 60-95
            import random
            total_score = random.randint(60, 95)
            
            result, created = FinalResult.objects.get_or_create(
                enrollment=enrollment,
                defaults={
                    'total_score': total_score,
                    'letter_grade': self._get_letter_grade(total_score),
                    'is_published': True,
                }
            )
            if created:
                self.stdout.write(f"  Created grade: {enrollment.student.student_no} - {result.letter_grade}")
    
    def _get_letter_grade(self, score):
        """Helper to convert score to letter grade"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def _create_demo_attendance(self):
        """Create 5-7 attendance records"""
        self.stdout.write("Creating demo attendance records...")
        from apps.enrollments.models import Enrollment
        from apps.attendance.models import AttendanceRecord
        from apps.accounts.models import User
        from datetime import date, timedelta
        
        enrollments = Enrollment.objects.filter(enroll_status='enrolled')[:7]
        admin_user = User.objects.filter(is_superuser=True).first()
        
        for enrollment in enrollments:
            # Create 3-5 attendance records per enrollment
            for i in range(4):
                attendance_date = date(2024, 10, 1) + timedelta(weeks=i)
                attendance, created = AttendanceRecord.objects.get_or_create(
                    enrollment=enrollment,
                    attendance_date=attendance_date,
                    defaults={
                        'status': 'present',
                        'recorded_by': admin_user,
                    }
                )
                if created:
                    self.stdout.write(f"  Attendance: {enrollment.student.student_no} - {attendance_date}")
    
    def _create_demo_warnings(self):
        """Create 3-5 warning records"""
        self.stdout.write("Creating demo warning records...")
        from apps.warnings.models import EarlyWarningResult
        from apps.students.models import Student
        from apps.semesters.models import Semester
        
        students = list(Student.objects.filter(status='active')[:5])
        semester = Semester.objects.get(academic_year='2024-2025', semester_type='fall')
        
        warning_data = [
            {'level': 'yellow', 'score': 35, 'factors': ['Low attendance']},
            {'level': 'orange', 'score': 55, 'factors': ['Low attendance', 'Missing assignments']},
            {'level': 'red', 'score': 75, 'factors': ['Critical attendance', 'Failing grades']},
            {'level': 'yellow', 'score': 40, 'factors': ['GPA drop']},
            {'level': 'orange', 'score': 60, 'factors': ['Low attendance', 'GPA drop']},
        ]
        
        for i, student in enumerate(students):
            data = warning_data[i % len(warning_data)]
            warning, created = EarlyWarningResult.objects.get_or_create(
                student=student,
                semester=semester,
                defaults={
                    'risk_score': data['score'],
                    'warning_level': data['level'],
                    'risk_factors': data['factors'],
                    'is_acknowledged': False,
                }
            )
            if created:
                self.stdout.write(f"  Created warning: {student.student_no} - {data['level']}")
    
    def _create_demo_announcements(self):
        """Create 3-5 announcements"""
        self.stdout.write("Creating demo announcements...")
        from apps.announcements.models import Announcement
        
        announcements_data = [
            {
                'title_en': 'Welcome to Fall 2024 Semester',
                'title_zh': '欢迎来到2024秋季学期',
                'content_en': 'Welcome all students to the new semester. Please check your course schedules.',
                'content_zh': '欢迎所有学生来到新学期。请查看您的课程表。',
                'priority': 'normal',
            },
            {
                'title_en': 'Midterm Examination Schedule',
                'title_zh': '期中考试时间表',
                'content_en': 'Midterm exams will be held from October 15-20. Please prepare accordingly.',
                'content_zh': '期中考试将于10月15日至20日举行。请做好准备。',
                'priority': 'high',
            },
            {
                'title_en': 'Holiday Notice - National Day',
                'title_zh': '国庆节放假通知',
                'content_en': 'The university will be closed from October 1-7 for National Day holiday.',
                'content_zh': '大学将在10月1日至7日国庆节放假。',
                'priority': 'high',
            },
            {
                'title_en': 'Library Hours Extended',
                'title_zh': '图书馆延长开放时间',
                'content_en': 'Library will now be open until 11 PM during exam weeks.',
                'content_zh': '考试周期间图书馆将开放至晚上11点。',
                'priority': 'normal',
            },
            {
                'title_en': 'COVID-19 Safety Guidelines',
                'title_zh': 'COVID-19安全指南',
                'content_en': 'Please follow all safety guidelines and wear masks in crowded areas.',
                'content_zh': '请遵守所有安全指南，在拥挤区域佩戴口罩。',
                'priority': 'urgent',
            },
        ]
        
        for data in announcements_data:
            announcement, created = Announcement.objects.get_or_create(
                title_en=data['title_en'],
                defaults={
                    'title_zh': data['title_zh'],
                    'content_en': data['content_en'],
                    'content_zh': data['content_zh'],
                    'priority': data['priority'],
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(f"  Created announcement: {data['title_en']}")
