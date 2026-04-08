"""
Management command to generate early warning alerts for students.

Usage:
    python manage.py generate_warnings [--semester SEMESTER_ID] [--all]
"""

import logging
from typing import Optional

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.semesters.models import Semester
from apps.warnings.risk_service import RiskCalculationService


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Generate early warning alerts for students based on risk factors'

    def add_arguments(self, parser):
        parser.add_argument(
            '--semester',
            type=int,
            help='Semester ID to generate warnings for (defaults to active semester)'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Generate warnings for all semesters, not just active ones'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be generated without creating records'
        )

    def handle(self, *args, **options):
        semester_id = options.get('semester')
        all_semesters = options.get('all')
        dry_run = options.get('dry_run')

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No records will be created'))

        if all_semesters:
            semesters = Semester.objects.all().order_by('-start_date')
        elif semester_id:
            try:
                semesters = [Semester.objects.get(pk=semester_id)]
            except Semester.DoesNotExist:
                raise CommandError(f'Semester with ID {semester_id} does not exist')
        else:
            # Default to active semester
            try:
                active_semester = Semester.objects.filter(is_active=True).first()
                if not active_semester:
                    raise CommandError('No active semester found. Use --semester or --all')
                semesters = [active_semester]
            except Semester.DoesNotExist:
                raise CommandError('No semesters found in the system')

        total_warnings = 0
        total_students = 0

        for semester in semesters:
            self.stdout.write(f'\nProcessing semester: {semester}')
            
            # Generate warnings for this semester
            if dry_run:
                # Just count students who would be processed
                from apps.students.models import Student
                student_count = Student.objects.filter(
                    enrollments__course_offering__semester=semester
                ).distinct().count()
                self.stdout.write(f'  Would process {student_count} students')
                total_students += student_count
            else:
                try:
                    count = RiskCalculationService.generate_warnings_for_semester(semester)
                    total_warnings += count
                    self.stdout.write(self.style.SUCCESS(f'  Generated warnings for {count} students'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  Error: {e}'))
                    logger.exception(f'Error generating warnings for semester {semester}')

        if dry_run:
            self.stdout.write(f'\n{self.style.WARNING(f"Dry run complete. Would process {total_students} students across {len(semesters)} semester(s).")}')
        else:
            self.stdout.write(f'\n{self.style.SUCCESS(f"Successfully generated warnings for {total_warnings} students across {len(semesters)} semester(s).")}')
