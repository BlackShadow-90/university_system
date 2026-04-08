"""
Management command to initialize system data.
Run: python manage.py init_system_data
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import Role, Permission, RolePermission
from apps.results.models import GradeScheme, GradeMapping
from apps.warnings.models import EarlyWarningRule
from apps.settings_app.models import GradePolicy


class Command(BaseCommand):
    help = 'Initialize system with default roles, permissions, grade schemes, and warning rules'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('Starting system initialization...'))
        
        with transaction.atomic():
            self.create_roles()
            self.create_grade_scheme()
            self.create_grade_policy()
            self.create_warning_rules()
        
        self.stdout.write(self.style.SUCCESS('System initialization completed successfully!'))
    
    def create_roles(self):
        """Create default roles"""
        self.stdout.write('Creating roles...')
        
        roles_data = [
            {'name': 'Administrator', 'code': 'admin', 'description': 'System administrator with full access'},
            {'name': 'Teacher', 'code': 'teacher', 'description': 'Faculty member who teaches courses'},
            {'name': 'Student', 'code': 'student', 'description': 'Student enrolled in courses'},
        ]
        
        for role_data in roles_data:
            Role.objects.get_or_create(
                code=role_data['code'],
                defaults=role_data
            )
        
        self.stdout.write(self.style.SUCCESS(f'  Created {len(roles_data)} roles'))
    
    def create_grade_scheme(self):
        """Create default grade scheme with mappings"""
        self.stdout.write('Creating grade scheme...')
        
        scheme, created = GradeScheme.objects.get_or_create(
            name='Standard 4.0 Scale',
            defaults={
                'is_default': True,
                'description': 'Standard 4.0 GPA scale with letter grades'
            }
        )
        
        # Grade mappings (letter grade, grade point, min %, max %, is_passing)
        mappings = [
            ('A', 4.0, 90, 100, True),
            ('A-', 3.7, 85, 89, True),
            ('B+', 3.3, 80, 84, True),
            ('B', 3.0, 75, 79, True),
            ('B-', 2.7, 70, 74, True),
            ('C+', 2.3, 65, 69, True),
            ('C', 2.0, 60, 64, True),
            ('D', 1.0, 50, 59, True),
            ('F', 0.0, 0, 49, False),
        ]
        
        for i, (letter, point, min_pct, max_pct, passing) in enumerate(mappings):
            GradeMapping.objects.get_or_create(
                scheme=scheme,
                letter_grade=letter,
                defaults={
                    'grade_point': point,
                    'min_percentage': min_pct,
                    'max_percentage': max_pct,
                    'is_passing': passing,
                    'order': len(mappings) - i  # Higher grades have higher order
                }
            )
        
        self.stdout.write(self.style.SUCCESS(f'  Created grade scheme with {len(mappings)} mappings'))
    
    def create_grade_policy(self):
        """Create default grade policy"""
        self.stdout.write('Creating grade policy...')
        
        GradePolicy.objects.get_or_create(
            name='Default Policy',
            defaults={
                'is_default': True,
                'max_gpa': 4.0,
                'passing_grade_point': 1.0,
                'gpa_warning_threshold': 2.0,
                'cgpa_warning_threshold': 2.0,
                'attendance_warning_threshold': 75.0,
                'gpa_drop_warning_threshold': 0.8,
                'description': 'Default grade policy for the institution'
            }
        )
        
        self.stdout.write(self.style.SUCCESS('  Created grade policy'))
    
    def create_warning_rules(self):
        """Create default early warning rules"""
        self.stdout.write('Creating warning rules...')
        
        rules_data = [
            {
                'code': 'ATTENDANCE_CRITICAL',
                'name': 'Critical Attendance Risk',
                'category': 'attendance',
                'threshold_value': 60,
                'comparison_operator': '<',
                'weight': 100,
                'severity': 'red',
                'description': 'Attendance below 60% - Critical intervention required'
            },
            {
                'code': 'ATTENDANCE_WARNING',
                'name': 'Low Attendance Warning',
                'category': 'attendance',
                'threshold_value': 75,
                'comparison_operator': '<',
                'weight': 50,
                'severity': 'orange',
                'description': 'Attendance below 75% - Monitoring required'
            },
            {
                'code': 'GPA_CRITICAL',
                'name': 'Critical GPA Risk',
                'category': 'gpa',
                'threshold_value': 1.5,
                'comparison_operator': '<',
                'weight': 100,
                'severity': 'red',
                'description': 'GPA below 1.5 - Critical academic risk'
            },
            {
                'code': 'GPA_WARNING',
                'name': 'Low GPA Warning',
                'category': 'gpa',
                'threshold_value': 2.0,
                'comparison_operator': '<',
                'weight': 75,
                'severity': 'orange',
                'description': 'GPA below 2.0 - Academic support recommended'
            },
            {
                'code': 'COURSE_FAILURES',
                'name': 'Multiple Course Failures',
                'category': 'course_failures',
                'threshold_value': 2,
                'comparison_operator': '>=',
                'weight': 75,
                'severity': 'orange',
                'description': '2 or more failed courses in current semester'
            },
            {
                'code': 'GPA_DROP',
                'name': 'Significant GPA Drop',
                'category': 'gpa_trend',
                'threshold_value': 0.8,
                'comparison_operator': '>',
                'weight': 50,
                'severity': 'yellow',
                'description': 'GPA dropped by more than 0.8 from previous semester'
            },
        ]
        
        for i, rule_data in enumerate(rules_data):
            EarlyWarningRule.objects.get_or_create(
                code=rule_data['code'],
                defaults={
                    'name': rule_data['name'],
                    'category': rule_data['category'],
                    'threshold_value': rule_data['threshold_value'],
                    'comparison_operator': rule_data['comparison_operator'],
                    'weight': rule_data['weight'],
                    'severity': rule_data['severity'],
                    'description': rule_data['description'],
                    'is_active': True,
                    'order': i
                }
            )
        
        self.stdout.write(self.style.SUCCESS(f'  Created {len(rules_data)} warning rules'))
