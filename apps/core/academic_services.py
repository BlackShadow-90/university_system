"""
Academic Calculation Service Layer

Centralized service for all academic calculations including:
- Assessment validation
- Score processing
- Final score calculation
- Grade mapping
- GPA/CGPA calculation
- Recalculation triggers
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Tuple
from django.db import transaction
from django.db.models import Sum, F
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class GradeScale:
    """
    Grade scale configuration for GPA calculation.
    Maps percentage ranges to letter grades and grade points.
    """
    
    # Standard 4.0 grade scale
    DEFAULT_SCALE = [
        {'min': 90, 'max': 100, 'grade': 'A', 'points': Decimal('4.0')},
        {'min': 85, 'max': 89, 'grade': 'A-', 'points': Decimal('3.7')},
        {'min': 80, 'max': 84, 'grade': 'B+', 'points': Decimal('3.3')},
        {'min': 75, 'max': 79, 'grade': 'B', 'points': Decimal('3.0')},
        {'min': 70, 'max': 74, 'grade': 'B-', 'points': Decimal('2.7')},
        {'min': 65, 'max': 69, 'grade': 'C+', 'points': Decimal('2.3')},
        {'min': 60, 'max': 64, 'grade': 'C', 'points': Decimal('2.0')},
        {'min': 55, 'max': 59, 'grade': 'C-', 'points': Decimal('1.7')},
        {'min': 50, 'max': 54, 'grade': 'D', 'points': Decimal('1.0')},
        {'min': 0, 'max': 49, 'grade': 'F', 'points': Decimal('0.0')},
    ]
    
    def __init__(self, scale_config: Optional[List[Dict]] = None):
        self.scale = scale_config or self.DEFAULT_SCALE
        
    def get_grade(self, percentage):
        """
        Get letter grade and grade points for a percentage.
        
        Args:
            percentage: Percentage score (can be Decimal or float)
            
        Returns:
            Tuple of (letter_grade, grade_points)
        """
        # Convert to float for comparison with scale items
        percentage_float = float(percentage) if percentage is not None else 0
        
        for scale_item in self.scale:
            if scale_item['min'] <= percentage_float <= scale_item['max']:
                return scale_item['grade'], scale_item['points']
        return 'F', Decimal('0.0')


class AssessmentValidationService:
    """
    Service for validating assessment components and their weights.
    Enforces hard rules for the assessment pipeline.
    """
    
    @staticmethod
    def validate_component_weights(course_offering, raise_error: bool = False) -> Tuple[bool, str]:
        """
        STRICT: Validate that assessment component weights sum to EXACTLY 100%.
        
        This is a hard requirement - final scores CANNOT be calculated unless
        components total exactly 100%.
        
        Args:
            course_offering: CourseOffering instance
            raise_error: If True, raises ValidationError instead of returning tuple
            
        Returns:
            Tuple of (is_valid, error_message)
            
        Raises:
            ValidationError: If raise_error=True and weights don't total 100%
        """
        from apps.assessments.models import AssessmentComponent
        
        components = AssessmentComponent.objects.filter(course_offering=course_offering)
        total_weight = components.aggregate(
            total=Sum('weight_percentage')
        )['total'] or Decimal('0')
        
        if total_weight != Decimal('100'):
            error_msg = f"Total weight must be exactly 100%, current: {total_weight}%. Cannot calculate final scores."
            if raise_error:
                raise ValidationError(error_msg)
            return False, error_msg
        
        # Also verify at least one component exists
        if not components.exists():
            error_msg = "No assessment components defined for this course offering."
            if raise_error:
                raise ValidationError(error_msg)
            return False, error_msg
        
        return True, ""
    
    @staticmethod
    def validate_all_components_have_scores(enrollment, raise_error: bool = False) -> Tuple[bool, str, List]:
        """
        Validate that all components have submitted scores for an enrollment.
        
        Args:
            enrollment: Enrollment instance
            raise_error: If True, raises ValidationError if any components missing scores
            
        Returns:
            Tuple of (is_valid, error_message, missing_components)
        """
        from apps.assessments.models import AssessmentComponent, AssessmentScore
        
        components = AssessmentComponent.objects.filter(
            course_offering=enrollment.course_offering
        )
        
        # Get all submitted scores for this enrollment
        submitted_scores = AssessmentScore.objects.filter(
            enrollment=enrollment,
            status='submitted'
        ).values_list('assessment_component_id', flat=True)
        
        missing = []
        for component in components:
            if component.pk not in submitted_scores:
                missing.append(component.name)
        
        if missing:
            error_msg = f"Missing scores for components: {', '.join(missing)}"
            if raise_error:
                raise ValidationError(error_msg)
            return False, error_msg, missing
        
        return True, "", []
    
    @staticmethod
    def validate_score(component, score: float, raise_error: bool = False) -> Tuple[bool, str]:
        """
        STRICT: Validate that a score is within acceptable range (0 to max_score).
        
        Args:
            component: AssessmentComponent instance
            score: Score value to validate
            raise_error: If True, raises ValidationError instead of returning tuple
            
        Returns:
            Tuple of (is_valid, error_message)
            
        Raises:
            ValidationError: If raise_error=True and score is invalid
        """
        if score is None:
            return True, ""  # None scores are allowed (representing missing data)
        
        if score < 0:
            error_msg = f"Score cannot be negative: {score}"
            if raise_error:
                raise ValidationError(error_msg)
            return False, error_msg
        
        # Convert to Decimal for comparison
        score_decimal = Decimal(str(score)) if score is not None else None
        max_score = Decimal(str(component.max_score))
        
        if score_decimal is not None and score_decimal > max_score:
            error_msg = f"Score {score} exceeds maximum allowed ({component.max_score}) for component '{component.name}'"
            if raise_error:
                raise ValidationError(error_msg)
            return False, error_msg
        
        return True, ""
    
    @staticmethod
    def validate_score_against_max_score(score_obj, raise_error: bool = False) -> Tuple[bool, str]:
        """
        Validate an AssessmentScore instance against its component's max_score.
        
        Args:
            score_obj: AssessmentScore instance
            raise_error: If True, raises ValidationError if score is invalid
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if score_obj.score is None:
            return True, ""
        
        return AssessmentValidationService.validate_score(
            score_obj.assessment_component,
            score_obj.score,  # Pass as is (Decimal) - validate_score will handle it
            raise_error=raise_error
        )
    
    @staticmethod
    def can_calculate_final_result(course_offering) -> Tuple[bool, str]:
        """
        Check if all prerequisites are met to calculate final results.
        
        Returns:
            Tuple of (can_calculate, reason_if_not)
        """
        # Rule 1: Must have exactly 100% weight total
        valid, error = AssessmentValidationService.validate_component_weights(course_offering)
        if not valid:
            return False, error
        
        return True, ""


class FinalScoreCalculationService:
    """
    Service for calculating final course scores from assessment components.
    """
    
    @staticmethod
    def calculate_weighted_score(enrollment, validate_weights: bool = True) -> Decimal:
        """
        Calculate weighted final score for an enrollment.
        
        Formula: weighted_score = sum(score/max_score * weight)
        
        Args:
            enrollment: Enrollment instance
            validate_weights: If True (default), enforces that component weights total 100%
            
        Returns:
            Weighted final score as Decimal
            
        Raises:
            ValidationError: If validate_weights=True and weights don't total 100%
        """
        from apps.assessments.models import AssessmentScore, AssessmentComponent
        
        # STRICT: Validate component weights total 100% before calculation
        if validate_weights:
            AssessmentValidationService.validate_component_weights(
                enrollment.course_offering, 
                raise_error=True
            )
        
        # Get all assessment components for this course offering
        components = AssessmentComponent.objects.filter(
            course_offering=enrollment.course_offering
        )
        
        if not components.exists():
            return Decimal('0')
        
        # Get all scores for this enrollment
        scores = AssessmentScore.objects.filter(
            enrollment=enrollment,
            status='submitted'
        ).select_related('assessment_component')
        
        # Create a lookup of scores by component
        score_lookup = {s.assessment_component_id: s for s in scores}
        
        weighted_sum = Decimal('0')
        
        for component in components:
            score_obj = score_lookup.get(component.pk)
            
            if score_obj and score_obj.score is not None:
                # STRICT: Validate score against max_score before using
                AssessmentValidationService.validate_score_against_max_score(
                    score_obj, 
                    raise_error=True
                )
                
                # Calculate normalized score (0-100 scale based on weight)
                normalized_score = (
                    Decimal(str(score_obj.score)) / 
                    component.max_score * 
                    component.weight_percentage
                )
                weighted_sum += normalized_score
        
        return weighted_sum.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @staticmethod
    def update_final_score(enrollment, validate_weights: bool = True) -> None:
        """
        DEPRECATED: Calculate and update final score for an enrollment.
        
        This method is deprecated because FinalResult is now the source of truth.
        Use FinalResultCalculationService.calculate_and_create_final_result() instead.
        
        Args:
            enrollment: Enrollment instance
            validate_weights: If True (default), enforces that component weights total 100%
        """
        import warnings
        warnings.warn(
            "update_final_score() is deprecated. Use FinalResultCalculationService.calculate_and_create_final_result() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        
        final_score = FinalScoreCalculationService.calculate_weighted_score(
            enrollment, 
            validate_weights=validate_weights
        )
        # Fix: Use _final_score field, not the property
        enrollment._final_score = final_score
        enrollment.save(update_fields=['_final_score'])


class FinalResultCalculationService:
    """
    Service for creating and updating FinalResult records.
    
    This is the ONLY authorized way to create/update final results.
    It enforces all pipeline rules:
    - Component weights must total exactly 100%
    - All scores must be validated against max_score
    - Results are linked to course offerings
    - Only published results are used for GPA/CGPA
    """
    
    @staticmethod
    @transaction.atomic
    def calculate_and_create_final_result(enrollment) -> 'FinalResult':
        """
        Calculate final result from assessment scores and create/update FinalResult record.
        
        This is the hardened pipeline entry point that enforces ALL rules.
        
        Args:
            enrollment: Enrollment instance
            
        Returns:
            Created or updated FinalResult instance
            
        Raises:
            ValidationError: If any validation rule is violated
        """
        from apps.results.models import FinalResult
        from apps.enrollments.models import Enrollment
        
        # Rule 0: Check readiness first (provides detailed diagnostics)
        readiness = ResultReadinessService.check_readiness(enrollment)
        if not readiness['can_calculate']:
            error_msg = "; ".join(readiness['reasons'])
            raise ValidationError(f"Result not ready for calculation: {error_msg}")
        
        # Rule 1: Validate component weights total exactly 100%
        AssessmentValidationService.validate_component_weights(
            enrollment.course_offering, 
            raise_error=True
        )
        
        # Rule 2: Validate all components have submitted scores
        has_all_scores, error_msg, missing = AssessmentValidationService.validate_all_components_have_scores(
            enrollment, 
            raise_error=False
        )
        if not has_all_scores:
            raise ValidationError(f"Cannot calculate final result: {error_msg}")
        
        # Rule 3: Calculate weighted final score (validates each score against max_score)
        final_score = FinalScoreCalculationService.calculate_weighted_score(
            enrollment, 
            validate_weights=False  # Already validated above
        )
        
        # Rule 4: Map to letter grade and grade points
        grade_scale = GradeScale()
        letter_grade, grade_point = grade_scale.get_grade_for_percentage(final_score)
        
        # Rule 5: Determine pass/fail status
        pass_fail_status = 'pass' if grade_point > 0 else 'fail'
        
        # Rule 6: Calculate quality points (grade_point × credit_hours)
        credit_hours = Decimal(str(enrollment.course_offering.course.credit_hours))
        quality_points = grade_point * credit_hours
        
        # Rule 7: Create or update FinalResult record (single source of truth)
        final_result, created = FinalResult.objects.update_or_create(
            enrollment=enrollment,
            defaults={
                'total_score': final_score,
                'letter_grade': letter_grade,
                'grade_point': grade_point,
                'pass_fail_status': pass_fail_status,
                'quality_points': quality_points,
                'is_published': False,  # Results start unpublished
                'published_at': None,
                'published_by': None,
            }
        )
        
        return final_result
    
    @staticmethod
    @transaction.atomic
    def publish_results(final_results, published_by=None):
        """
        Publish multiple final results.
        
        Args:
            final_results: QuerySet or list of FinalResult instances
            published_by: User who is publishing the results
            
        Returns:
            Number of results published
        """
        from django.utils import timezone
        
        published_count = 0
        
        for final_result in final_results:
            # Use the publish method to ensure pipeline runs
            result = final_result.publish(triggered_by=published_by)
            if result['success']:
                published_count += 1
        
        return published_count
    
    @staticmethod
    @transaction.atomic  
    def bulk_calculate_for_offering(course_offering, calculate_only: bool = True) -> List['FinalResult']:
        """
        Calculate final results for all enrollments in a course offering.
        
        Args:
            course_offering: CourseOffering instance
            calculate_only: If True, only calculate without publishing
            
        Returns:
            List of created/updated FinalResult instances
            
        Raises:
            ValidationError: If component weights don't total 100%
        """
        from apps.enrollments.models import Enrollment
        
        # Validate weights first
        AssessmentValidationService.validate_component_weights(
            course_offering, 
            raise_error=True
        )
        
        enrollments = Enrollment.objects.filter(
            course_offering=course_offering,
            enroll_status='enrolled'
        ).select_related('student', 'course_offering__course')
        
        results = []
        for enrollment in enrollments:
            try:
                final_result = FinalResultCalculationService.calculate_and_create_final_result(enrollment)
                results.append(final_result)
            except ValidationError as e:
                # Log but continue with other enrollments
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Skipping enrollment {enrollment.pk}: {e}")
                continue
        
        return results


class GPACalculationService:
    """
    Service for calculating GPA and CGPA.
    
    CRITICAL: Only published FinalResult records are used for GPA/CGPA calculations.
    This ensures that draft or pending results don't affect student records.
    """
    
    def __init__(self):
        self.grade_scale = GradeScale()
    
    def calculate_semester_gpa(self, student, semester) -> Tuple[Decimal, int]:
        """
        Calculate GPA for a specific semester using ONLY published final results.
        
        Formula: GPA = sum(grade_point × credit_hours) / total_credits
        
        Args:
            student: Student instance
            semester: Semester instance
            
        Returns:
            Tuple of (GPA, total_credits)
        """
        from apps.results.models import FinalResult
        
        # STRICT: Only use PUBLISHED final results for GPA calculation
        published_results = FinalResult.objects.filter(
            enrollment__student=student,
            enrollment__course_offering__semester=semester,
            is_published=True,
            grade_point__isnull=False
        ).select_related(
            'enrollment__course_offering__course'
        )
        
        if not published_results.exists():
            return Decimal('0.00'), 0
        
        total_points = Decimal('0')
        total_credits = Decimal('0')
        
        for final_result in published_results:
            enrollment = final_result.enrollment
            credit_hours = Decimal(str(enrollment.course_offering.course.credit_hours))
            grade_points = final_result.grade_point
            
            total_points += grade_points * credit_hours
            total_credits += credit_hours
        
        if total_credits == 0:
            return Decimal('0.00'), 0
        
        gpa = (total_points / total_credits).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        
        return gpa, int(total_credits)
    
    def calculate_cgpa(self, student, up_to_semester=None) -> Tuple[Decimal, int]:
        """
        Calculate cumulative GPA using ONLY published final results.
        
        Args:
            student: Student instance
            up_to_semester: Optional semester to limit calculation up to
            
        Returns:
            Tuple of (CGPA, total_credits)
        """
        from apps.results.models import FinalResult
        from apps.semesters.models import Semester
        
        # STRICT: Only use PUBLISHED final results for CGPA calculation
        queryset = FinalResult.objects.filter(
            enrollment__student=student,
            is_published=True,
            grade_point__isnull=False
        ).select_related(
            'enrollment__course_offering__course',
            'enrollment__course_offering__semester'
        )
        
        if up_to_semester:
            queryset = queryset.filter(
                enrollment__course_offering__semester__start_date__lte=up_to_semester.start_date
            )
        
        # Group by course to handle repeats (keep highest grade)
        course_best_grades = {}
        
        for final_result in queryset:
            enrollment = final_result.enrollment
            course_id = enrollment.course_offering.course_id
            grade_points = final_result.grade_point
            credits = Decimal(str(enrollment.course_offering.course.credit_hours))
            
            if course_id not in course_best_grades:
                course_best_grades[course_id] = {
                    'grade_points': grade_points,
                    'credits': credits
                }
            elif grade_points > course_best_grades[course_id]['grade_points']:
                course_best_grades[course_id]['grade_points'] = grade_points
                course_best_grades[course_id]['credits'] = credits
        
        if not course_best_grades:
            return Decimal('0.00'), 0
        
        total_points = sum(
            data['grade_points'] * data['credits']
            for data in course_best_grades.values()
        )
        total_credits = sum(data['credits'] for data in course_best_grades.values())
        
        if total_credits == 0:
            return Decimal('0.00'), 0
        
        cgpa = (total_points / total_credits).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        
        return cgpa, int(total_credits)
    
    def _get_grade_points(self, final_score: Decimal) -> Decimal:
        """
        Get grade points for a final score percentage.
        
        Args:
            final_score: Final score percentage
            
        Returns:
            Grade points as Decimal
        """
        _, points = self.grade_scale.get_grade_for_percentage(final_score)
        return points


class GradeCalculationService(GPACalculationService):
    """
    Alias for GPACalculationService for backward compatibility.
    Provides grade calculation functionality.
    """
    pass


class AcademicRecalculationService:
    """
    Service for triggering recalculations when data changes.
    """
    
    @staticmethod
    @transaction.atomic
    def recalculate_enrollment(enrollment, triggered_by=None) -> None:
        """
        Recalculate final score and related metrics for an enrollment.
        
        Note: This creates/updates the FinalResult record but does NOT publish it.
        GPA/CGPA will only reflect changes after the result is published.
        
        Args:
            enrollment: Enrollment instance
            triggered_by: Optional user who triggered this recalculation
        """
        import time
        from .models import CalculationLogService, SystemCalculationLog
        
        start_time = time.time()
        
        # Use hardened pipeline to calculate and create/update FinalResult
        try:
            FinalResultCalculationService.calculate_and_create_final_result(enrollment)
            
            # Log success
            duration_ms = int((time.time() - start_time) * 1000)
            CalculationLogService.log_success(
                action_type=SystemCalculationLog.ACTION_RESULT_RECALC,
                message=f"Recalculated final result for {enrollment.student.user.get_full_name()} in {enrollment.course_offering.course.code}",
                student=enrollment.student,
                enrollment=enrollment,
                semester=enrollment.course_offering.semester,
                course_offering=enrollment.course_offering,
                details={
                    'final_score': str(enrollment.final_score) if enrollment.final_score else None,
                    'enrollment_id': enrollment.id,
                    'course_code': enrollment.course_offering.course.code
                },
                triggered_by=triggered_by,
                duration_ms=duration_ms
            )
        except ValidationError as e:
            # Log failure
            duration_ms = int((time.time() - start_time) * 1000)
            CalculationLogService.log_failure(
                action_type=SystemCalculationLog.ACTION_RESULT_RECALC,
                message=f"Failed to recalculate result for {enrollment.student.user.get_full_name()}",
                error=e,
                student=enrollment.student,
                enrollment=enrollment,
                semester=enrollment.course_offering.semester,
                course_offering=enrollment.course_offering,
                details={
                    'validation_error': str(e),
                    'enrollment_id': enrollment.id
                },
                triggered_by=triggered_by,
                duration_ms=duration_ms
            )
            raise  # Re-raise so caller knows it failed
        except Exception as e:
            # Log unexpected failure
            duration_ms = int((time.time() - start_time) * 1000)
            CalculationLogService.log_failure(
                action_type=SystemCalculationLog.ACTION_RESULT_RECALC,
                message=f"Unexpected error recalculating result for {enrollment.student.user.get_full_name()}",
                error=e,
                student=enrollment.student,
                enrollment=enrollment,
                semester=enrollment.course_offering.semester,
                course_offering=enrollment.course_offering,
                details={
                    'error_type': type(e).__name__,
                    'enrollment_id': enrollment.id
                },
                triggered_by=triggered_by,
                duration_ms=duration_ms
            )
            raise
    
    @staticmethod
    @transaction.atomic
    def recalculate_all_for_student(student, triggered_by=None) -> None:
        """
        Recalculate all academic metrics for a student.
        
        Args:
            student: Student instance
            triggered_by: Optional user who triggered this recalculation
        """
        import time
        from apps.results.models import FinalResult
        from .models import CalculationLogService, SystemCalculationLog
        
        start_time = time.time()
        
        try:
            # Get all published final results for this student
            published_results = FinalResult.objects.filter(
                enrollment__student=student,
                is_published=True
            ).select_related(
                'enrollment__course_offering__semester'
            ).order_by('enrollment__course_offering__semester__start_date')
            
            # Recalculate semester GPAs
            semesters_processed = set()
            gpa_service = GPACalculationService()
            
            for final_result in published_results:
                semester = final_result.enrollment.course_offering.semester
                if semester.pk not in semesters_processed:
                    semester_gpa, credits = gpa_service.calculate_semester_gpa(student, semester)
                    
                    # Update student's semester record if exists
                    from apps.students.models import StudentSemesterRecord
                    try:
                        record = StudentSemesterRecord.objects.get(
                            student=student,
                            semester=semester
                        )
                        record.gpa = semester_gpa
                        record.credits_earned = credits
                        record.save(update_fields=['gpa', 'credits_earned'])
                    except StudentSemesterRecord.DoesNotExist:
                        pass
                    
                    semesters_processed.add(semester.pk)
            
            # Recalculate CGPA
            cgpa, total_credits = gpa_service.calculate_cgpa(student)
            
            # Update student record
            student.cgpa = cgpa
            student.total_credits = total_credits
            student.save(update_fields=['cgpa', 'total_credits'])
            
            # Log success
            duration_ms = int((time.time() - start_time) * 1000)
            CalculationLogService.log_success(
                action_type=SystemCalculationLog.ACTION_GPA_RECALC,
                message=f"Recalculated GPA/CGPA for {student.user.get_full_name()}",
                student=student,
                details={
                    'cgpa': str(cgpa),
                    'total_credits': total_credits,
                    'semesters_processed': len(semesters_processed)
                },
                triggered_by=triggered_by,
                duration_ms=duration_ms
            )
            
        except Exception as e:
            # Log failure
            duration_ms = int((time.time() - start_time) * 1000)
            CalculationLogService.log_failure(
                action_type=SystemCalculationLog.ACTION_GPA_RECALC,
                message=f"Failed to recalculate GPA/CGPA for {student.user.get_full_name()}",
                error=e,
                student=student,
                details={'error_type': type(e).__name__},
                triggered_by=triggered_by,
                duration_ms=duration_ms
            )
            raise


class EarlyWarningCalculationService:
    """
    Service for calculating early warning indicators.
    """
    
    WARNING_LEVELS = {
        'green': {'min': 70, 'label': 'Good Standing'},
        'yellow': {'min': 60, 'label': 'At Risk'},
        'orange': {'min': 50, 'label': 'High Risk'},
        'red': {'min': 0, 'label': 'Critical Risk'},
    }
    
    @staticmethod
    def calculate_attendance_risk(enrollment) -> Decimal:
        """
        Calculate attendance risk percentage for an enrollment.
        
        Returns 0 (no risk) if attendance data is missing or incomplete,
        rather than producing unstable results.
        
        Args:
            enrollment: Enrollment instance
            
        Returns:
            Risk score as Decimal (0-100), or None if data insufficient
        """
        # Guard: Check if enrollment has attendance tracking
        if not enrollment:
            return None
            
        # Guard: Skip if no attendance records exist yet
        total_classes = enrollment.total_classes or 0
        if total_classes == 0:
            # No attendance data recorded yet - neutral risk
            return None
        
        attendance_pct = enrollment.attendance_percentage or Decimal('0')
        
        # Risk increases as attendance decreases
        if attendance_pct >= 80:
            return Decimal('0')
        elif attendance_pct >= 70:
            return Decimal('25')
        elif attendance_pct >= 60:
            return Decimal('50')
        elif attendance_pct >= 50:
            return Decimal('75')
        else:
            return Decimal('100')
    
    @staticmethod
    def calculate_academic_risk(enrollment) -> Decimal:
        """
        Calculate academic risk based on current performance.
        
        Uses FinalResult as the single source of truth for grades.
        Falls back to preliminary calculation from available marks if no FinalResult.
        Returns None if insufficient data to calculate.
        
        Args:
            enrollment: Enrollment instance
            
        Returns:
            Risk score as Decimal (0-100), or None if data insufficient
        """
        from apps.results.models import FinalResult
        from apps.assessments.models import AssessmentScore
        
        # Guard: Check enrollment exists
        if not enrollment:
            return None
        
        # Strategy 1: Use FinalResult if available and published
        try:
            final_result = FinalResult.objects.get(enrollment=enrollment)
            if final_result.total_score is not None:
                final_score = final_result.total_score
            else:
                # FinalResult exists but no score - try preliminary
                final_score = None
        except FinalResult.DoesNotExist:
            final_score = None
        
        # Strategy 2: Calculate preliminary score from available marks
        if final_score is None:
            # Check if any assessment scores exist
            has_scores = AssessmentScore.objects.filter(
                enrollment=enrollment,
                score__isnull=False
            ).exists()
            
            if not has_scores:
                # No marks entered yet - insufficient data
                return None
            
            # Try to calculate preliminary score
            try:
                final_score = FinalScoreCalculationService.calculate_weighted_score(
                    enrollment, 
                    validate_weights=False  # Allow incomplete setups for early warnings
                )
            except ValidationError:
                # Cannot calculate even preliminary score
                return None
        
        # Guard: Validate we have a usable score
        if final_score is None:
            return None
        
        # Risk increases as score decreases
        if final_score >= 70:
            return Decimal('0')
        elif final_score >= 60:
            return Decimal('25')
        elif final_score >= 50:
            return Decimal('50')
        elif final_score >= 40:
            return Decimal('75')
        else:
            return Decimal('100')
    
    @staticmethod
    def determine_warning_level(attendance_risk: Decimal, academic_risk: Decimal) -> str:
        """
        Determine overall warning level based on risk scores.
        
        Args:
            attendance_risk: Attendance risk score (0-100) or None
            academic_risk: Academic risk score (0-100) or None
            
        Returns:
            Warning level string ('green', 'yellow', 'orange', 'red')
        """
        # If neither risk can be calculated, default to green (no warning)
        if attendance_risk is None and academic_risk is None:
            return 'green'
        
        # Use available risks (treat None as 0 - no risk)
        max_risk = max(
            attendance_risk or Decimal('0'),
            academic_risk or Decimal('0')
        )
        
        if max_risk >= 75:
            return 'red'
        elif max_risk >= 50:
            return 'orange'
        elif max_risk >= 25:
            return 'yellow'
        else:
            return 'green'
    
    @classmethod
    def update_early_warning(cls, enrollment, triggered_by=None) -> Optional['EarlyWarningResult']:
        """
        Update or create early warning result for an enrollment.
        
        Only creates/updates if sufficient data is available.
        Returns None if skipped due to insufficient data.
        
        Args:
            enrollment: Enrollment instance
            triggered_by: Optional user who triggered this calculation
            
        Returns:
            EarlyWarningResult instance or None if skipped
        """
        import time
        from apps.warnings.models import EarlyWarningResult
        from .models import CalculationLogService, SystemCalculationLog
        
        start_time = time.time()
        
        # Guard: Skip if enrollment is not valid/active
        if not enrollment or enrollment.enroll_status != 'enrolled':
            CalculationLogService.log_skipped(
                action_type=SystemCalculationLog.ACTION_WARNING_RECALC,
                message=f"Skipped warning calculation - enrollment not active",
                student=enrollment.student if enrollment else None,
                enrollment=enrollment,
                details={'enroll_status': enrollment.enroll_status if enrollment else None},
                triggered_by=triggered_by
            )
            return None
        
        # Guard: Skip if student or semester not available
        if not enrollment.student or not enrollment.course_offering or not enrollment.course_offering.semester:
            CalculationLogService.log_skipped(
                action_type=SystemCalculationLog.ACTION_WARNING_RECALC,
                message=f"Skipped warning calculation - missing student or semester data",
                student=enrollment.student if enrollment else None,
                enrollment=enrollment,
                details={'missing_data': True},
                triggered_by=triggered_by
            )
            return None
        
        try:
            # Calculate risks (may return None if insufficient data)
            attendance_risk = cls.calculate_attendance_risk(enrollment)
            academic_risk = cls.calculate_academic_risk(enrollment)
            
            # Guard: Skip if absolutely no data available
            if attendance_risk is None and academic_risk is None:
                # No attendance data, no marks - course just started
                CalculationLogService.log_skipped(
                    action_type=SystemCalculationLog.ACTION_WARNING_RECALC,
                    message=f"Skipped warning calculation - no attendance or academic data available",
                    student=enrollment.student,
                    enrollment=enrollment,
                    semester=enrollment.course_offering.semester,
                    details={
                        'attendance_risk': None,
                        'academic_risk': None,
                        'reason': 'Insufficient data for warning calculation'
                    },
                    triggered_by=triggered_by
                )
                return None
            
            # Determine warning level
            warning_level = cls.determine_warning_level(attendance_risk, academic_risk)
            
            # Build risk factors list for detailed explanation
            risk_factors = []
            if attendance_risk is not None and attendance_risk > 0:
                risk_factors.append({
                    'type': 'attendance',
                    'score': float(attendance_risk),
                    'reason': f'Attendance below threshold ({enrollment.attendance_percentage:.1f}%)'
                })
            if academic_risk is not None and academic_risk > 0:
                risk_factors.append({
                    'type': 'academic',
                    'score': float(academic_risk),
                    'reason': 'Academic performance concerns'
                })
            
            result, created = EarlyWarningResult.objects.update_or_create(
                student=enrollment.student,
                semester=enrollment.course_offering.semester,
                defaults={
                    'warning_level': warning_level,
                    'attendance_risk_score': attendance_risk or Decimal('0'),
                    'gpa_risk_score': academic_risk or Decimal('0'),
                    'risk_factors': risk_factors,
                    'calculated_at': timezone.now()
                }
            )
            
            # Log success
            duration_ms = int((time.time() - start_time) * 1000)
            CalculationLogService.log_success(
                action_type=SystemCalculationLog.ACTION_WARNING_RECALC,
                message=f"Updated early warning for {enrollment.student.user.get_full_name()}: {warning_level}",
                student=enrollment.student,
                enrollment=enrollment,
                semester=enrollment.course_offering.semester,
                details={
                    'warning_level': warning_level,
                    'attendance_risk': float(attendance_risk) if attendance_risk else None,
                    'academic_risk': float(academic_risk) if academic_risk else None,
                    'risk_factors': risk_factors,
                    'created': created
                },
                triggered_by=triggered_by,
                duration_ms=duration_ms
            )
            
            return result
            
        except Exception as e:
            # Log failure
            duration_ms = int((time.time() - start_time) * 1000)
            CalculationLogService.log_failure(
                action_type=SystemCalculationLog.ACTION_WARNING_RECALC,
                message=f"Failed to update early warning for {enrollment.student.user.get_full_name()}",
                error=e,
                student=enrollment.student,
                enrollment=enrollment,
                semester=enrollment.course_offering.semester,
                details={'error_type': type(e).__name__},
                triggered_by=triggered_by,
                duration_ms=duration_ms
            )
            raise


class AcademicPipelineService:
    """
    Centralized service for processing all academic updates.
    
    Ensures consistent pipeline execution regardless of where the update originates:
    - Teacher portal
    - Admin portal  
    - Bulk uploads
    - Direct edits
    - Scripts
    - Custom views
    
    Every update path should use these methods to guarantee consistent behavior.
    """
    
    @staticmethod
    @transaction.atomic
    def process_mark_update(assessment_score, triggered_by=None) -> Dict[str, any]:
        """
        Process a mark update through the complete academic pipeline.
        
        Chain: validate → update final result → update GPA → update warning → refresh status
        
        Args:
            assessment_score: AssessmentScore instance that was updated/created
            triggered_by: Optional user who triggered this update
            
        Returns:
            Dict with processing results and status
        """
        import time
        from .models import CalculationLogService, SystemCalculationLog
        from apps.assessments.models import AssessmentScore
        
        start_time = time.time()
        enrollment = assessment_score.enrollment
        results = {
            'success': False,
            'final_result_updated': False,
            'gpa_updated': False,
            'warning_updated': False,
            'errors': [],
            'messages': []
        }
        
        try:
            # Step 1: Validate the mark
            is_valid, error_msg = AssessmentValidationService.validate_score_against_max_score(
                assessment_score, raise_error=False
            )
            if not is_valid:
                results['errors'].append(f"Invalid score: {error_msg}")
                return results
            
            results['messages'].append("Mark validated successfully")
            
            # Step 2: Update final result (if ready)
            try:
                readiness = ResultReadinessService.check_readiness(enrollment)
                if readiness['can_calculate']:
                    AcademicRecalculationService.recalculate_enrollment(enrollment, triggered_by)
                    results['final_result_updated'] = True
                    results['messages'].append("Final result recalculated")
                else:
                    results['messages'].append("Final result not ready - missing components")
            except ValidationError as e:
                results['errors'].append(f"Failed to recalculate result: {e}")
            
            # Step 3: Update GPA (only if result is published)
            try:
                if hasattr(enrollment, 'final_result') and enrollment.final_result and enrollment.final_result.is_published:
                    AcademicRecalculationService.recalculate_all_for_student(enrollment.student, triggered_by)
                    results['gpa_updated'] = True
                    results['messages'].append("GPA/CGPA updated")
                else:
                    results['messages'].append("GPA not updated - result not published")
            except Exception as e:
                results['errors'].append(f"Failed to update GPA: {e}")
            
            # Step 4: Update warning (always try)
            try:
                warning = EarlyWarningCalculationService.update_early_warning(enrollment, triggered_by)
                if warning:
                    results['warning_updated'] = True
                    results['messages'].append(f"Warning updated: {warning.warning_level}")
                else:
                    results['messages'].append("Warning not generated - insufficient data")
            except Exception as e:
                results['errors'].append(f"Failed to update warning: {e}")
            
            results['success'] = len(results['errors']) == 0
            
            # Log the pipeline execution
            duration_ms = int((time.time() - start_time) * 1000)
            if results['success']:
                CalculationLogService.log_success(
                    action_type=SystemCalculationLog.ACTION_MARK_SYNC,
                    message=f"Processed mark update for {enrollment.student.user.get_full_name()}",
                    student=enrollment.student,
                    enrollment=enrollment,
                    semester=enrollment.course_offering.semester,
                    course_offering=enrollment.course_offering,
                    details={
                        'component': assessment_score.assessment_component.name,
                        'score': str(assessment_score.score),
                        'pipeline_results': results
                    },
                    triggered_by=triggered_by,
                    duration_ms=duration_ms
                )
            else:
                CalculationLogService.log_failure(
                    action_type=SystemCalculationLog.ACTION_MARK_SYNC,
                    message=f"Failed to process mark update for {enrollment.student.user.get_full_name()}",
                    error=Exception("; ".join(results['errors'])),
                    student=enrollment.student,
                    enrollment=enrollment,
                    semester=enrollment.course_offering.semester,
                    course_offering=enrollment.course_offering,
                    details={
                        'component': assessment_score.assessment_component.name,
                        'score': str(assessment_score.score),
                        'errors': results['errors']
                    },
                    triggered_by=triggered_by,
                    duration_ms=duration_ms
                )
            
            return results
            
        except Exception as e:
            # Log unexpected failure
            duration_ms = int((time.time() - start_time) * 1000)
            CalculationLogService.log_failure(
                action_type=SystemCalculationLog.ACTION_MARK_SYNC,
                message=f"Unexpected error processing mark update for {enrollment.student.user.get_full_name()}",
                error=e,
                student=enrollment.student,
                enrollment=enrollment,
                semester=enrollment.course_offering.semester,
                course_offering=enrollment.course_offering,
                details={'error_type': type(e).__name__},
                triggered_by=triggered_by,
                duration_ms=duration_ms
            )
            results['errors'].append(f"Unexpected error: {e}")
            return results
    
    @staticmethod
    @transaction.atomic
    def process_attendance_update(attendance_record, triggered_by=None) -> Dict[str, any]:
        """
        Process an attendance update through the complete academic pipeline.
        
        Chain: validate → recalculate attendance % → update warning if needed
        
        Args:
            attendance_record: AttendanceRecord instance that was updated/created
            triggered_by: Optional user who triggered this update
            
        Returns:
            Dict with processing results and status
        """
        import time
        from .models import CalculationLogService, SystemCalculationLog
        
        start_time = time.time()
        enrollment = attendance_record.enrollment
        results = {
            'success': False,
            'attendance_updated': False,
            'warning_updated': False,
            'errors': [],
            'messages': []
        }
        
        try:
            # Step 1: Attendance validation happens in model.full_clean()
            results['messages'].append("Attendance validated successfully")
            
            # Step 2: Recalculate attendance stats (happens automatically in save)
            # But we'll ensure it's done and get the updated values
            enrollment.recalculate_attendance_stats()
            results['attendance_updated'] = True
            results['messages'].append(f"Attendance updated: {enrollment.attendance_percentage:.1f}%")
            
            # Step 3: Update warning (attendance changes can affect warning level)
            try:
                warning = EarlyWarningCalculationService.update_early_warning(enrollment, triggered_by)
                if warning:
                    results['warning_updated'] = True
                    results['messages'].append(f"Warning updated: {warning.warning_level}")
                else:
                    results['messages'].append("Warning not generated - insufficient data")
            except Exception as e:
                results['errors'].append(f"Failed to update warning: {e}")
            
            results['success'] = len(results['errors']) == 0
            
            # Log the pipeline execution
            duration_ms = int((time.time() - start_time) * 1000)
            if results['success']:
                CalculationLogService.log_success(
                    action_type=SystemCalculationLog.ACTION_ATTENDANCE_RECALC,
                    message=f"Processed attendance update for {enrollment.student.user.get_full_name()}",
                    student=enrollment.student,
                    enrollment=enrollment,
                    semester=enrollment.course_offering.semester,
                    course_offering=enrollment.course_offering,
                    details={
                        'status': attendance_record.status,
                        'date': str(attendance_record.attendance_date),
                        'attendance_percentage': str(enrollment.attendance_percentage),
                        'pipeline_results': results
                    },
                    triggered_by=triggered_by,
                    duration_ms=duration_ms
                )
            else:
                CalculationLogService.log_failure(
                    action_type=SystemCalculationLog.ACTION_ATTENDANCE_RECALC,
                    message=f"Failed to process attendance update for {enrollment.student.user.get_full_name()}",
                    error=Exception("; ".join(results['errors'])),
                    student=enrollment.student,
                    enrollment=enrollment,
                    semester=enrollment.course_offering.semester,
                    course_offering=enrollment.course_offering,
                    details={
                        'status': attendance_record.status,
                        'errors': results['errors']
                    },
                    triggered_by=triggered_by,
                    duration_ms=duration_ms
                )
            
            return results
            
        except Exception as e:
            # Log unexpected failure
            duration_ms = int((time.time() - start_time) * 1000)
            CalculationLogService.log_failure(
                action_type=SystemCalculationLog.ACTION_ATTENDANCE_RECALC,
                message=f"Unexpected error processing attendance update for {enrollment.student.user.get_full_name()}",
                error=e,
                student=enrollment.student,
                enrollment=enrollment,
                semester=enrollment.course_offering.semester,
                course_offering=enrollment.course_offering,
                details={'error_type': type(e).__name__},
                triggered_by=triggered_by,
                duration_ms=duration_ms
            )
            results['errors'].append(f"Unexpected error: {e}")
            return results
    
    @staticmethod
    @transaction.atomic
    def process_result_publish(final_result, triggered_by=None) -> Dict[str, any]:
        """
        Process a result publication through the complete academic pipeline.
        
        Chain: validate → publish → update GPA → update warning → refresh status
        
        Args:
            final_result: FinalResult instance being published
            triggered_by: Optional user who triggered this publication
            
        Returns:
            Dict with processing results and status
        """
        import time
        from .models import CalculationLogService, SystemCalculationLog
        
        start_time = time.time()
        enrollment = final_result.enrollment
        results = {
            'success': False,
            'result_published': False,
            'gpa_updated': False,
            'warning_updated': False,
            'errors': [],
            'messages': []
        }
        
        try:
            # Step 1: Validate result is ready for publication
            if not final_result.total_score:
                results['errors'].append("Cannot publish result - no total score calculated")
                return results
            
            results['messages'].append("Result validated for publication")
            
            # Step 2: Publish the result
            final_result.is_published = True
            final_result.published_at = timezone.now()
            final_result.published_by = triggered_by
            final_result.save(update_fields=['is_published', 'published_at', 'published_by'])
            results['result_published'] = True
            results['messages'].append("Result published successfully")
            
            # Step 3: Update GPA (published results affect GPA)
            try:
                AcademicRecalculationService.recalculate_all_for_student(enrollment.student, triggered_by)
                results['gpa_updated'] = True
                results['messages'].append("GPA/CGPA updated")
            except Exception as e:
                results['errors'].append(f"Failed to update GPA: {e}")
            
            # Step 4: Update warning (published grades can affect warning level)
            try:
                warning = EarlyWarningCalculationService.update_early_warning(enrollment, triggered_by)
                if warning:
                    results['warning_updated'] = True
                    results['messages'].append(f"Warning updated: {warning.warning_level}")
                else:
                    results['messages'].append("Warning not generated - insufficient data")
            except Exception as e:
                results['errors'].append(f"Failed to update warning: {e}")
            
            results['success'] = len(results['errors']) == 0
            
            # Log the pipeline execution
            duration_ms = int((time.time() - start_time) * 1000)
            if results['success']:
                CalculationLogService.log_success(
                    action_type=SystemCalculationLog.ACTION_RESULT_PUBLISH,
                    message=f"Published result for {enrollment.student.user.get_full_name()} in {enrollment.course_offering.course.code}",
                    student=enrollment.student,
                    enrollment=enrollment,
                    semester=enrollment.course_offering.semester,
                    course_offering=enrollment.course_offering,
                    details={
                        'total_score': str(final_result.total_score),
                        'letter_grade': final_result.letter_grade,
                        'pipeline_results': results
                    },
                    triggered_by=triggered_by,
                    duration_ms=duration_ms
                )
            else:
                CalculationLogService.log_failure(
                    action_type=SystemCalculationLog.ACTION_RESULT_PUBLISH,
                    message=f"Failed to publish result for {enrollment.student.user.get_full_name()}",
                    error=Exception("; ".join(results['errors'])),
                    student=enrollment.student,
                    enrollment=enrollment,
                    semester=enrollment.course_offering.semester,
                    course_offering=enrollment.course_offering,
                    details={
                        'errors': results['errors']
                    },
                    triggered_by=triggered_by,
                    duration_ms=duration_ms
                )
            
            return results
            
        except Exception as e:
            # Log unexpected failure
            duration_ms = int((time.time() - start_time) * 1000)
            CalculationLogService.log_failure(
                action_type=SystemCalculationLog.ACTION_RESULT_PUBLISH,
                message=f"Unexpected error publishing result for {enrollment.student.user.get_full_name()}",
                error=e,
                student=enrollment.student,
                enrollment=enrollment,
                semester=enrollment.course_offering.semester,
                course_offering=enrollment.course_offering,
                details={'error_type': type(e).__name__},
                triggered_by=triggered_by,
                duration_ms=duration_ms
            )
            results['errors'].append(f"Unexpected error: {e}")
            return results


class ResultReadinessService:
    """
    Service for checking if an enrollment is ready for final result calculation.
    
    Provides detailed diagnostic information about what's missing or invalid,
    making it easy for teachers and admins to understand why results can't be calculated.
    """
    
    @staticmethod
    def check_readiness(enrollment) -> Dict[str, any]:
        """
        Check if enrollment is ready for final result calculation.
        
        Returns a detailed report with:
        - can_calculate: bool - True if all requirements are met
        - missing_components: list - Components without submitted marks
        - weights_valid: bool - Whether component weights total 100%
        - weight_total: Decimal - Actual total weight percentage
        - invalid_scores: list - Scores that fail validation
        - reasons: list - Human-readable explanations of issues
        
        Args:
            enrollment: Enrollment instance to check
            
        Returns:
            Dict containing readiness status and detailed diagnostics
        """
        from apps.assessments.models import AssessmentComponent, AssessmentScore
        
        report = {
            'can_calculate': False,
            'missing_components': [],
            'weights_valid': False,
            'weight_total': Decimal('0'),
            'invalid_scores': [],
            'components_total': 0,
            'components_with_scores': 0,
            'reasons': []
        }
        
        # Get all components for this course offering
        components = AssessmentComponent.objects.filter(
            course_offering=enrollment.course_offering
        )
        
        report['components_total'] = components.count()
        
        if report['components_total'] == 0:
            report['reasons'].append(_('No assessment components defined for this course'))
            return report
        
        # Check 1: Component weights must total 100%
        weight_total = sum(c.weight_percentage for c in components)
        report['weight_total'] = Decimal(str(weight_total)).quantize(Decimal('0.01'))
        report['weights_valid'] = (weight_total == 100)
        
        if not report['weights_valid']:
            if weight_total < 100:
                report['reasons'].append(
                    _('Component weights total %(total)s%% (missing %(missing)s%%)') % {
                        'total': weight_total,
                        'missing': 100 - weight_total
                    }
                )
            else:
                report['reasons'].append(
                    _('Component weights total %(total)s%% (exceeds by %(excess)s%%)') % {
                        'total': weight_total,
                        'excess': weight_total - 100
                    }
                )
        
        # Check 2: All components must have submitted scores
        existing_scores = AssessmentScore.objects.filter(
            enrollment=enrollment,
            assessment_component__in=components
        ).select_related('assessment_component')
        
        scored_component_ids = set(
            existing_scores.values_list('assessment_component_id', flat=True)
        )
        
        for component in components:
            if component.id not in scored_component_ids:
                report['missing_components'].append({
                    'id': component.id,
                    'name': component.name,
                    'type': component.assessment_type,  # Fixed: was component_type
                    'weight': component.weight_percentage
                })
            else:
                report['components_with_scores'] += 1
        
        if report['missing_components']:
            component_names = [c['name'] for c in report['missing_components']]
            report['reasons'].append(
                _('Missing marks for: %(components)s') % {
                    'components': ', '.join(component_names)
                }
            )
        
        # Check 3: Validate existing scores against max_score
        for score in existing_scores:
            if score.score is not None:
                try:
                    AssessmentValidationService.validate_score_against_max_score(
                        score, raise_error=True
                    )
                except ValidationError as e:
                    report['invalid_scores'].append({
                        'component_name': score.assessment_component.name,
                        'score': score.score,
                        'max_score': score.assessment_component.max_score,
                        'error': str(e)
                    })
                    report['reasons'].append(
                        _('Invalid score for %(component)s: %(error)s') % {
                            'component': score.assessment_component.name,
                            'error': str(e)
                        }
                    )
        
        # Final determination: can calculate if all checks pass
        report['can_calculate'] = (
            report['weights_valid'] and
            len(report['missing_components']) == 0 and
            len(report['invalid_scores']) == 0 and
            report['components_total'] > 0
        )
        
        if report['can_calculate']:
            report['reasons'].append(_('Ready for result generation'))
        
        return report
    
    @staticmethod
    def check_offering_readiness(course_offering) -> Dict[str, any]:
        """
        Check readiness for all enrollments in a course offering.
        
        Returns aggregate statistics and per-enrollment details.
        
        Args:
            course_offering: CourseOffering instance to check
            
        Returns:
            Dict containing aggregate stats and enrollment details
        """
        from apps.enrollments.models import Enrollment
        
        enrollments = Enrollment.objects.filter(
            course_offering=course_offering,
            enroll_status='enrolled'
        )
        
        total = enrollments.count()
        ready = 0
        not_ready = 0
        enrollment_details = []
        
        for enrollment in enrollments:
            readiness = ResultReadinessService.check_readiness(enrollment)
            
            if readiness['can_calculate']:
                ready += 1
            else:
                not_ready += 1
            
            enrollment_details.append({
                'enrollment_id': enrollment.id,
                'student_name': enrollment.student.user.get_full_name(),
                'student_no': enrollment.student.student_no,
                'can_calculate': readiness['can_calculate'],
                'missing_count': len(readiness['missing_components']),
                'reasons': readiness['reasons']
            })
        
        return {
            'total_enrollments': total,
            'ready_count': ready,
            'not_ready_count': not_ready,
            'all_ready': (not_ready == 0 and total > 0),
            'enrollments': enrollment_details
        }


class WarningManagementService:
    """
    Service for managing warning operations (manual creation, clearing, teacher flags).
    
    Separates warning management business logic from views.
    """
    
    # Default warning rules configuration
    DEFAULT_RULES = [
        {
            'code': 'gpa_critical',
            'name': 'Critical Low GPA',
            'category': 'gpa',
            'threshold_value': 1.5,
            'comparison_operator': '<',
            'severity': 'red',
            'weight': 30,
            'description': 'GPA below 1.5 - Critical academic performance'
        },
        {
            'code': 'gpa_warning',
            'name': 'Low GPA Warning',
            'category': 'gpa',
            'threshold_value': 2.0,
            'comparison_operator': '<',
            'severity': 'orange',
            'weight': 20,
            'description': 'GPA below 2.0 - Warning level'
        },
        {
            'code': 'cgpa_critical',
            'name': 'Critical Low CGPA',
            'category': 'cgpa',
            'threshold_value': 2.0,
            'comparison_operator': '<',
            'severity': 'red',
            'weight': 25,
            'description': 'CGPA below 2.0 - Critical cumulative performance'
        },
        {
            'code': 'cgpa_warning',
            'name': 'Low CGPA Warning',
            'category': 'cgpa',
            'threshold_value': 2.5,
            'comparison_operator': '<',
            'severity': 'orange',
            'weight': 15,
            'description': 'CGPA below 2.5 - Warning level'
        },
        {
            'code': 'attendance_critical',
            'name': 'Critical Attendance',
            'category': 'attendance',
            'threshold_value': 60,
            'comparison_operator': '<',
            'severity': 'red',
            'weight': 25,
            'description': 'Attendance below 60% - Critical absence'
        },
        {
            'code': 'attendance_warning',
            'name': 'Low Attendance Warning',
            'category': 'attendance',
            'threshold_value': 75,
            'comparison_operator': '<',
            'severity': 'orange',
            'weight': 15,
            'description': 'Attendance below 75% - Warning level'
        },
        {
            'code': 'course_failures',
            'name': 'Failed Courses',
            'category': 'course_failures',
            'threshold_value': 1,
            'comparison_operator': '>=',
            'severity': 'orange',
            'weight': 15,
            'description': 'Failed courses detected'
        },
        {
            'code': 'gpa_trend',
            'name': 'GPA Drop',
            'category': 'gpa_trend',
            'threshold_value': -0.50,
            'comparison_operator': '<',
            'severity': 'orange',
            'weight': 10,
            'description': 'Significant GPA decline from previous semester'
        },
        {
            'code': 'missing_assessment',
            'name': 'Missing Assessments',
            'category': 'missing_assessment',
            'threshold_value': 1,
            'comparison_operator': '>=',
            'severity': 'yellow',
            'weight': 10,
            'description': 'Missing or incomplete assessments'
        },
    ]
    
    @staticmethod
    def ensure_default_rules_exist() -> int:
        """
        Create default warning rules if they don't exist.
        
        Returns:
            Number of rules created
        """
        from apps.warnings.models import EarlyWarningRule
        
        created_count = 0
        for rule_data in WarningManagementService.DEFAULT_RULES:
            _, created = EarlyWarningRule.objects.get_or_create(
                code=rule_data['code'],
                defaults=rule_data
            )
            if created:
                created_count += 1
        
        return created_count
    
    @staticmethod
    def create_manual_warning(student, semester, warning_level: str, reason: str, 
                              created_by: Optional[str] = None) -> 'EarlyWarningResult':
        """
        Create or update a manual warning for a student.
        
        Args:
            student: Student instance
            semester: Semester instance
            warning_level: 'yellow', 'orange', or 'red'
            reason: Explanation for the warning
            created_by: Name of person creating the warning (optional)
            
        Returns:
            Created or updated EarlyWarningResult
        """
        from apps.warnings.models import EarlyWarningResult
        
        # Calculate risk score based on level
        risk_score = {
            'yellow': 30,
            'orange': 50,
            'red': 70
        }.get(warning_level, 30)
        
        # Build risk factor entry
        risk_factor = {
            'rule': 'Manual Assignment',
            'category': 'teacher_flag',
            'value': 'N/A',
            'threshold': 'N/A',
            'severity': warning_level,
            'reason': reason,
            'created_by': created_by or 'Admin'
        }
        
        result, created = EarlyWarningResult.objects.get_or_create(
            student=student,
            semester=semester,
            defaults={
                'warning_level': warning_level,
                'risk_score': risk_score,
                'risk_factors': [risk_factor],
                'recommendations': ['Manual intervention required'],
                'teacher_flag_risk_score': risk_score,
                'calculated_at': timezone.now()
            }
        )
        
        if not created:
            # Update existing warning
            result.warning_level = warning_level
            result.risk_score = risk_score
            
            # Append to risk factors
            if isinstance(result.risk_factors, list):
                result.risk_factors.append({
                    **risk_factor,
                    'rule': 'Manual Assignment (Updated)'
                })
            else:
                result.risk_factors = [risk_factor]
            
            result.save()
        
        return result
    
    @staticmethod
    def clear_warning(warning: 'EarlyWarningResult', cleared_by: Optional[str] = None) -> None:
        """
        Clear/resolve a warning for a student.
        
        Args:
            warning: EarlyWarningResult instance to clear
            cleared_by: Name of person clearing the warning (optional)
        """
        warning.warning_level = 'green'
        warning.risk_score = 0
        warning.risk_factors = [{
            'rule': 'Warning Cleared',
            'category': 'admin_action',
            'reason': f'Cleared by {cleared_by or "admin"}',
            'cleared_at': timezone.now().isoformat()
        }]
        warning.recommendations = ['Warning has been resolved']
        warning.save()
    
    @staticmethod
    def flag_student_by_teacher(student, semester, severity: str, reason: str, 
                                teacher_name: str) -> 'EarlyWarningResult':
        """
        Teacher flags a student as at-risk.
        
        Args:
            student: Student instance
            semester: Semester instance
            severity: 'yellow', 'orange', or 'red'
            reason: Teacher's reason for flagging
            teacher_name: Name of the teacher flagging
            
        Returns:
            Created or updated EarlyWarningResult
        """
        from apps.warnings.models import EarlyWarningResult
        
        # Calculate risk score based on severity
        risk_score = {
            'yellow': 30,
            'orange': 50,
            'red': 70
        }.get(severity, 30)
        
        # Build teacher flag risk factor
        flag_factor = {
            'rule': 'Teacher Flag',
            'category': 'teacher_flag',
            'value': 'N/A',
            'threshold': 'N/A',
            'severity': severity,
            'reason': reason,
            'teacher': teacher_name,
            'flagged_at': timezone.now().isoformat()
        }
        
        result, created = EarlyWarningResult.objects.get_or_create(
            student=student,
            semester=semester,
            defaults={
                'warning_level': severity,
                'risk_score': risk_score,
                'risk_factors': [flag_factor],
                'recommendations': ['Teacher has flagged this student for attention'],
                'teacher_flag_risk_score': risk_score,
                'calculated_at': timezone.now()
            }
        )
        
        if not created:
            # Add teacher flag to existing warning
            result.teacher_flag_risk_score = risk_score
            
            if isinstance(result.risk_factors, list):
                result.risk_factors.append({
                    **flag_factor,
                    'rule': 'Teacher Flag (Updated)'
                })
            else:
                result.risk_factors = [flag_factor]
            
            # Upgrade warning level if teacher flag is more severe
            severity_order = {'green': 0, 'yellow': 1, 'orange': 2, 'red': 3}
            if severity_order.get(severity, 0) > severity_order.get(result.warning_level, 0):
                result.warning_level = severity
            
            result.save()
        
        return result


# Import timezone for early warning updates
from django.utils import timezone
