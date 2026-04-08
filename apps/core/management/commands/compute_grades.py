"""
Management command to compute final grades for enrollments
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.translation import gettext as _

from apps.enrollments.models import Enrollment
from apps.core.academic_services import GradeCalculationService
from apps.results.models import FinalResult


class Command(BaseCommand):
    help = 'Compute final grades for enrollments from assessment scores'

    def add_arguments(self, parser):
        parser.add_argument(
            '--enrollment-id',
            type=int,
            help='Compute grade for specific enrollment ID'
        )
        parser.add_argument(
            '--semester-id',
            type=int,
            help='Compute grades for all enrollments in a semester'
        )
        parser.add_argument(
            '--publish',
            action='store_true',
            help='Publish the results after calculation'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be calculated without saving'
        )

    def handle(self, *args, **options):
        enrollment_id = options.get('enrollment_id')
        semester_id = options.get('semester_id')
        publish = options.get('publish')
        dry_run = options.get('dry_run')
        
        # Get enrollments to process
        if enrollment_id:
            enrollments = Enrollment.objects.filter(pk=enrollment_id)
        elif semester_id:
            enrollments = Enrollment.objects.filter(
                course_offering__semester_id=semester_id
            )
        else:
            # Get all enrollments that don't have final results yet
            enrollments = Enrollment.objects.filter(
                final_result__isnull=True
            )
        
        if not enrollments.exists():
            self.stdout.write(self.style.WARNING('No enrollments found to process.'))
            return
        
        self.stdout.write(f"Processing {enrollments.count()} enrollments...")
        
        processed = 0
        failed = 0
        
        for enrollment in enrollments:
            try:
                result = self._process_enrollment(enrollment, dry_run)
                if result:
                    processed += 1
                    if not dry_run:
                        self.stdout.write(
                            f"  {enrollment.student.student_no} - "
                            f"{enrollment.course_offering.course.code}: "
                            f"{result.letter_grade} ({result.total_score:.2f})"
                        )
                else:
                    failed += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f"  {enrollment.student.student_no} - "
                            f"Could not calculate grade (missing scores)"
                        )
                    )
            except Exception as e:
                failed += 1
                self.stdout.write(
                    self.style.ERROR(
                        f"  {enrollment.student.student_no} - Error: {str(e)}"
                    )
                )
        
        self.stdout.write(self.style.SUCCESS(
            f"\nCompleted: {processed} processed, {failed} failed"
        ))
    
    def _process_enrollment(self, enrollment, dry_run):
        """Process a single enrollment"""
        # Calculate final percentage
        final_percentage = GradeCalculationService.calculate_enrollment_final_grade(enrollment)
        
        if final_percentage is None:
            return None
        
        # Get grade mappings for the program
        grade_mappings = GradeMapping.objects.filter(
            program=enrollment.student.program
        ).order_by('-max_percentage')
        
        if not grade_mappings.exists():
            raise Exception("No grade mappings found for student's program")
        
        # Apply grade mapping
        letter_grade, grade_point, is_passing = GradeCalculationService.apply_grade_mapping(
            final_percentage, grade_mappings
        )
        
        if dry_run:
            # Return mock result for display
            class MockResult:
                def __init__(self, letter, score):
                    self.letter_grade = letter
                    self.total_score = score
            return MockResult(letter_grade, final_percentage)
        
        # Create or update final result
        final_result, created = FinalResult.objects.update_or_create(
            enrollment=enrollment,
            defaults={
                'total_score': final_percentage,
                'letter_grade': letter_grade,
                'grade_point': grade_point,
                'is_passing': is_passing,
                'is_published': False,
            }
        )
        
        # Update enrollment pass/fail status (deprecated field)
        enrollment._pass_fail_status = 'pass' if is_passing else 'fail'
        enrollment.save(update_fields=['_pass_fail_status'])
        
        return final_result
