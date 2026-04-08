"""
Management command to recompute CGPA for students
"""
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from apps.students.models import Student
from apps.core.academic_services import GradeCalculationService


class Command(BaseCommand):
    help = 'Recompute CGPA for students'

    def add_arguments(self, parser):
        parser.add_argument(
            '--student-id',
            type=int,
            help='Recompute CGPA for specific student'
        )
        parser.add_argument(
            '--program-id',
            type=int,
            help='Recompute CGPA for all students in a program'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be calculated without saving'
        )

    def handle(self, *args, **options):
        student_id = options.get('student_id')
        program_id = options.get('program_id')
        dry_run = options.get('dry_run')
        
        # Get students to process
        if student_id:
            students = Student.objects.filter(pk=student_id)
        elif program_id:
            students = Student.objects.filter(program_id=program_id)
        else:
            students = Student.objects.all()
        
        if not students.exists():
            self.stdout.write(self.style.WARNING('No students found to process.'))
            return
        
        self.stdout.write(f"Processing {students.count()} students...")
        
        for student in students:
            old_cgpa = student.cgpa
            old_credits = student.total_credits_earned
            
            # Recompute CGPA
            new_cgpa = GradeCalculationService.recompute_student_cgpa(student)
            
            # Refresh student data from database
            student.refresh_from_db()
            new_credits = student.total_credits_earned
            
            if dry_run:
                self.stdout.write(
                    f"  {student.student_no} - {student.get_full_name()}: "
                    f"CGPA {old_cgpa} -> {new_cgpa}, "
                    f"Credits {old_credits} -> {new_credits}"
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  {student.student_no} - {student.get_full_name()}: "
                        f"CGPA {old_cgpa} -> {new_cgpa}, "
                        f"Credits {old_credits} -> {new_credits}"
                    )
                )
        
        self.stdout.write(self.style.SUCCESS("\nCGPA recomputation completed!"))
