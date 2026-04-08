"""
Management command to publish semester results
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.translation import gettext as _
from django.utils import timezone

from apps.enrollments.models import Enrollment
from apps.results.models import FinalResult
from apps.notifications.models import Notification
from apps.core.academic_services import GradeCalculationService


class Command(BaseCommand):
    help = 'Publish semester results and notify students'

    def add_arguments(self, parser):
        parser.add_argument(
            'semester_id',
            type=int,
            help='Semester ID to publish results for'
        )
        parser.add_argument(
            '--notify',
            action='store_true',
            default=True,
            help='Send notifications to students'
        )

    def handle(self, *args, **options):
        semester_id = options['semester_id']
        notify = options['notify']
        
        # Get enrollments with final results
        enrollments = Enrollment.objects.filter(
            course_offering__semester_id=semester_id,
            final_result__isnull=False,
            final_result__is_published=False
        ).select_related('student', 'student__user', 'course_offering', 'course_offering__course', 'final_result')
        
        if not enrollments.exists():
            self.stdout.write(
                self.style.WARNING('No unpublished results found for this semester.')
            )
            return
        
        self.stdout.write(f"Publishing {enrollments.count()} results...")
        
        published_count = 0
        
        with transaction.atomic():
            for enrollment in enrollments:
                # Publish the result using the pipeline method
                final_result = enrollment.final_result
                result = final_result.publish(triggered_by=None)
                if result['success']:
                    published_count += 1
                
                # Create notification if enabled
                if notify and enrollment.student.user:
                    Notification.objects.create(
                        user=enrollment.student.user,
                        title=_("Grade Published"),
                        message=_("Your grade for %(course)s has been published: %(grade)s") % {
                            'course': enrollment.course_offering.course.get_title(),
                            'grade': final_result.letter_grade
                        },
                        notification_type='grade',
                        related_object_type='FinalResult',
                        related_object_id=final_result.id
                    )
                
                self.stdout.write(
                    f"  Published: {enrollment.student.student_no} - "
                    f"{enrollment.course_offering.course.code}: "
                    f"{final_result.letter_grade}"
                )
            
            # Recompute CGPA for all affected students
            affected_students = set(e.student for e in enrollments)
            self.stdout.write(f"\nRecomputing CGPA for {len(affected_students)} students...")
            
            for student in affected_students:
                old_cgpa = student.cgpa
                GradeCalculationService.recompute_student_cgpa(student)
                student.refresh_from_db()
                self.stdout.write(
                    f"  {student.student_no}: CGPA {old_cgpa} -> {student.cgpa}"
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f"\nSuccessfully published {published_count} results!"
            )
        )
        
        if notify:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Notifications sent to {len(affected_students)} students."
                )
            )
