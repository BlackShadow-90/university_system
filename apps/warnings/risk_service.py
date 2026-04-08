"""
Early Warning System - Risk Calculation Service

Implements rule-based risk scoring with real data from:
- GPA/CGPA calculations
- Attendance records
- Course failures
- GPA trends (sudden drops)
- Missing assessments
"""

from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from django.db import transaction
from django.utils import timezone

from apps.students.models import Student
from apps.semesters.models import Semester
from apps.enrollments.models import Enrollment
from apps.academic.models import StudentAcademicStatus, FinalResult
from apps.attendance.models import AttendanceRecord
from apps.assessments.models import AssessmentComponent, AssessmentScore
from apps.warnings.models import EarlyWarningRule, EarlyWarningResult


class RiskCalculationService:
    """
    Calculates risk scores based on weighted risk factors.
    
    Risk Score Formula:
    - Each factor contributes (severity_weight * normalized_deviation) to total
    - Total score is 0-100 scale
    - Warning levels: Green(0-25), Yellow(26-50), Orange(51-75), Red(76-100)
    """
    
    # Default weights for risk factors (can be overridden by database rules)
    DEFAULT_WEIGHTS = {
        'gpa': Decimal('20.00'),
        'cgpa': Decimal('25.00'),
        'attendance': Decimal('20.00'),
        'course_failures': Decimal('15.00'),
        'gpa_trend': Decimal('10.00'),
        'missing_assessment': Decimal('10.00'),
    }
    
    # Default thresholds
    DEFAULT_THRESHOLDS = {
        'gpa': Decimal('2.00'),           # GPA below 2.0 is at-risk
        'cgpa': Decimal('2.00'),          # CGPA below 2.0 is at-risk
        'attendance': Decimal('75.00'),   # Attendance below 75% is at-risk
        'course_failures': Decimal('1'),  # 1 or more failures is concerning
        'gpa_trend': Decimal('-0.50'),    # GPA drop of 0.5 or more
        'missing_assessment': Decimal('1'), # 1 or more missing assessments
    }
    
    @classmethod
    def calculate_student_risk(cls, student: Student, semester: Semester) -> Dict:
        """
        Calculate comprehensive risk score for a student in a semester.
        Returns dict with individual scores and total risk score.
        """
        # Get active rules from database
        rules = cls._get_active_rules()
        
        # Calculate individual risk factors
        risk_factors = []
        
        # 1. GPA Risk
        gpa_risk = cls._calculate_gpa_risk(student, semester, rules.get('gpa'))
        if gpa_risk['triggered']:
            risk_factors.append({
                'category': 'gpa',
                'name': 'Low Semester GPA',
                'value': str(gpa_risk['value']),
                'threshold': str(gpa_risk['threshold']),
                'score': float(gpa_risk['score']),
                'description': f"GPA {gpa_risk['value']} is below threshold {gpa_risk['threshold']}"
            })
        
        # 2. CGPA Risk
        cgpa_risk = cls._calculate_cgpa_risk(student, semester, rules.get('cgpa'))
        if cgpa_risk['triggered']:
            risk_factors.append({
                'category': 'cgpa',
                'name': 'Low Cumulative GPA',
                'value': str(cgpa_risk['value']),
                'threshold': str(cgpa_risk['threshold']),
                'score': float(cgpa_risk['score']),
                'description': f"CGPA {cgpa_risk['value']} is below threshold {cgpa_risk['threshold']}"
            })
        
        # 3. Attendance Risk
        attendance_risk = cls._calculate_attendance_risk(student, semester, rules.get('attendance'))
        if attendance_risk['triggered']:
            risk_factors.append({
                'category': 'attendance',
                'name': 'Low Attendance',
                'value': str(attendance_risk['value']),
                'threshold': str(attendance_risk['threshold']),
                'score': float(attendance_risk['score']),
                'description': f"Attendance {attendance_risk['value']}% is below {attendance_risk['threshold']}%"
            })
        
        # 4. Course Failure Risk
        failure_risk = cls._calculate_failure_risk(student, semester, rules.get('course_failures'))
        if failure_risk['triggered']:
            risk_factors.append({
                'category': 'course_failures',
                'name': 'Failed Courses',
                'value': str(failure_risk['value']),
                'threshold': str(failure_risk['threshold']),
                'score': float(failure_risk['score']),
                'description': f"{failure_risk['value']} failed course(s) this semester"
            })
        
        # 5. GPA Trend Risk (sudden drop)
        trend_risk = cls._calculate_trend_risk(student, semester, rules.get('gpa_trend'))
        if trend_risk['triggered']:
            risk_factors.append({
                'category': 'gpa_trend',
                'name': 'Sudden GPA Drop',
                'value': str(trend_risk['value']),
                'threshold': str(trend_risk['threshold']),
                'score': float(trend_risk['score']),
                'description': f"GPA dropped by {abs(trend_risk['value'])} from previous semester"
            })
        
        # 6. Missing Assessment Risk
        missing_risk = cls._calculate_missing_assessment_risk(student, semester, rules.get('missing_assessment'))
        if missing_risk['triggered']:
            risk_factors.append({
                'category': 'missing_assessment',
                'name': 'Missing Assessments',
                'value': str(missing_risk['value']),
                'threshold': str(missing_risk['threshold']),
                'score': float(missing_risk['score']),
                'description': f"{missing_risk['value']} missing assessment(s)"
            })
        
        # Calculate total risk score
        total_score = sum(f['score'] for f in risk_factors)
        
        # Determine warning level
        warning_level = cls._determine_warning_level(total_score)
        
        # Generate recommendations
        recommendations = cls._generate_recommendations(risk_factors)
        
        return {
            'total_score': round(total_score, 2),
            'warning_level': warning_level,
            'risk_factors': risk_factors,
            'recommendations': recommendations,
            'category_scores': {
                'gpa': float(gpa_risk['score']),
                'cgpa': float(cgpa_risk['score']),
                'attendance': float(attendance_risk['score']),
                'course_failures': float(failure_risk['score']),
                'trend': float(trend_risk['score']),
                'missing_assessments': float(missing_risk['score']),
            }
        }
    
    @classmethod
    def _get_active_rules(cls) -> Dict[str, Optional[EarlyWarningRule]]:
        """Fetch active rules from database."""
        rules = {}
        categories = ['gpa', 'cgpa', 'attendance', 'course_failures', 'gpa_trend', 'missing_assessment']
        
        for category in categories:
            try:
                rule = EarlyWarningRule.objects.get(category=category, is_active=True)
                rules[category] = rule
            except EarlyWarningRule.DoesNotExist:
                rules[category] = None
        
        return rules
    
    @classmethod
    def _calculate_gpa_risk(cls, student: Student, semester: Semester, 
                           rule: Optional[EarlyWarningRule]) -> Dict:
        """Calculate risk score for low GPA."""
        threshold = rule.threshold_value if rule else cls.DEFAULT_THRESHOLDS['gpa']
        weight = rule.weight if rule else cls.DEFAULT_WEIGHTS['gpa']
        
        # Get student's GPA for this semester
        try:
            status = StudentAcademicStatus.objects.get(
                student=student,
                semester=semester
            )
            gpa = status.gpa
        except StudentAcademicStatus.DoesNotExist:
            gpa = Decimal('4.00')  # Assume good if no data
        
        if gpa < threshold:
            # Calculate severity based on how far below threshold
            deviation = float(threshold - gpa)
            max_deviation = float(threshold)  # Worst case is GPA of 0
            severity = min(deviation / max_deviation, 1.0) if max_deviation > 0 else 1.0
            score = float(weight) * severity
            
            return {
                'triggered': True,
                'value': gpa,
                'threshold': threshold,
                'score': Decimal(str(score)),
                'severity': severity
            }
        
        return {'triggered': False, 'value': gpa, 'threshold': threshold, 'score': Decimal('0.00')}
    
    @classmethod
    def _calculate_cgpa_risk(cls, student: Student, semester: Semester,
                            rule: Optional[EarlyWarningRule]) -> Dict:
        """Calculate risk score for low CGPA."""
        threshold = rule.threshold_value if rule else cls.DEFAULT_THRESHOLDS['cgpa']
        weight = rule.weight if rule else cls.DEFAULT_WEIGHTS['cgpa']
        
        try:
            status = StudentAcademicStatus.objects.get(
                student=student,
                semester=semester
            )
            cgpa = status.cgpa
        except StudentAcademicStatus.DoesNotExist:
            cgpa = Decimal('4.00')
        
        if cgpa < threshold:
            deviation = float(threshold - cgpa)
            max_deviation = float(threshold)
            severity = min(deviation / max_deviation, 1.0) if max_deviation > 0 else 1.0
            score = float(weight) * severity
            
            return {
                'triggered': True,
                'value': cgpa,
                'threshold': threshold,
                'score': Decimal(str(score)),
                'severity': severity
            }
        
        return {'triggered': False, 'value': cgpa, 'threshold': threshold, 'score': Decimal('0.00')}
    
    @classmethod
    def _calculate_attendance_risk(cls, student: Student, semester: Semester,
                                   rule: Optional[EarlyWarningRule]) -> Dict:
        """Calculate risk score for low attendance."""
        threshold = rule.threshold_value if rule else cls.DEFAULT_THRESHOLDS['attendance']
        weight = rule.weight if rule else cls.DEFAULT_WEIGHTS['attendance']
        
        # Get enrollments for this semester
        enrollments = Enrollment.objects.filter(
            student=student,
            course_offering__semester=semester
        )
        
        if not enrollments.exists():
            return {'triggered': False, 'value': Decimal('100'), 'threshold': threshold, 'score': Decimal('0.00')}
        
        # Calculate average attendance
        total_attendance = sum(e.attendance_percentage for e in enrollments)
        avg_attendance = Decimal(str(total_attendance / len(enrollments)))
        
        if avg_attendance < threshold:
            deviation = float(threshold - avg_attendance)
            max_deviation = float(threshold)  # Worst case is 0% attendance
            severity = min(deviation / max_deviation, 1.0) if max_deviation > 0 else 1.0
            score = float(weight) * severity
            
            return {
                'triggered': True,
                'value': avg_attendance,
                'threshold': threshold,
                'score': Decimal(str(score)),
                'severity': severity
            }
        
        return {'triggered': False, 'value': avg_attendance, 'threshold': threshold, 'score': Decimal('0.00')}
    
    @classmethod
    def _calculate_failure_risk(cls, student: Student, semester: Semester,
                               rule: Optional[EarlyWarningRule]) -> Dict:
        """Calculate risk score for failed courses."""
        threshold = rule.threshold_value if rule else cls.DEFAULT_THRESHOLDS['course_failures']
        weight = rule.weight if rule else cls.DEFAULT_WEIGHTS['course_failures']
        
        # Count failed courses
        failed_courses = FinalResult.objects.filter(
            enrollment__student=student,
            enrollment__course_offering__semester=semester,
            is_pass=False
        ).count()
        
        if failed_courses >= threshold:
            # More failures = higher risk, capped at weight
            severity = min(failed_courses / float(threshold + 2), 1.0)
            score = float(weight) * severity
            
            return {
                'triggered': True,
                'value': failed_courses,
                'threshold': threshold,
                'score': Decimal(str(score)),
                'severity': severity
            }
        
        return {'triggered': False, 'value': failed_courses, 'threshold': threshold, 'score': Decimal('0.00')}
    
    @classmethod
    def _calculate_trend_risk(cls, student: Student, semester: Semester,
                             rule: Optional[EarlyWarningRule]) -> Dict:
        """Calculate risk score for sudden GPA drop."""
        threshold = rule.threshold_value if rule else cls.DEFAULT_THRESHOLDS['gpa_trend']
        weight = rule.weight if rule else cls.DEFAULT_WEIGHTS['gpa_trend']
        
        # Get current and previous semester GPA
        try:
            current_status = StudentAcademicStatus.objects.get(
                student=student,
                semester=semester
            )
            current_gpa = current_status.gpa
            
            # Find previous semester
            prev_semester = Semester.objects.filter(
                end_date__lt=semester.start_date
            ).order_by('-end_date').first()
            
            if prev_semester:
                prev_status = StudentAcademicStatus.objects.get(
                    student=student,
                    semester=prev_semester
                )
                prev_gpa = prev_status.gpa
                
                # Calculate drop
                gpa_change = float(current_gpa) - float(prev_gpa)
                
                # Trigger if drop is significant (negative and exceeds threshold magnitude)
                if gpa_change < 0 and abs(gpa_change) >= abs(float(threshold)):
                    severity = min(abs(gpa_change) / 2.0, 1.0)  # Max drop of 2.0 = full severity
                    score = float(weight) * severity
                    
                    return {
                        'triggered': True,
                        'value': Decimal(str(gpa_change)),
                        'threshold': threshold,
                        'score': Decimal(str(score)),
                        'severity': severity
                    }
        except (StudentAcademicStatus.DoesNotExist, Semester.DoesNotExist):
            pass
        
        return {'triggered': False, 'value': Decimal('0'), 'threshold': threshold, 'score': Decimal('0.00')}
    
    @classmethod
    def _calculate_missing_assessment_risk(cls, student: Student, semester: Semester,
                                          rule: Optional[EarlyWarningRule]) -> Dict:
        """Calculate risk score for missing assessments."""
        threshold = rule.threshold_value if rule else cls.DEFAULT_THRESHOLDS['missing_assessment']
        weight = rule.weight if rule else cls.DEFAULT_WEIGHTS['missing_assessment']
        
        # Get all required assessments for student's courses
        enrollments = Enrollment.objects.filter(
            student=student,
            course_offering__semester=semester
        )
        
        missing_count = 0
        for enrollment in enrollments:
            # Get all components for this course
            components = AssessmentComponent.objects.filter(
                course_offering=enrollment.course_offering
            )
            
            for component in components:
                # Check if score exists
                if not AssessmentScore.objects.filter(
                    enrollment=enrollment,
                    assessment_component=component
                ).exists():
                    missing_count += 1
        
        if missing_count >= threshold:
            severity = min(missing_count / (float(threshold) + 3), 1.0)
            score = float(weight) * severity
            
            return {
                'triggered': True,
                'value': missing_count,
                'threshold': threshold,
                'score': Decimal(str(score)),
                'severity': severity
            }
        
        return {'triggered': False, 'value': missing_count, 'threshold': threshold, 'score': Decimal('0.00')}
    
    @classmethod
    def _determine_warning_level(cls, total_score: float) -> str:
        """Determine warning level based on total risk score."""
        if total_score <= 25:
            return 'green'
        elif total_score <= 50:
            return 'yellow'
        elif total_score <= 75:
            return 'orange'
        else:
            return 'red'
    
    @classmethod
    def _generate_recommendations(cls, risk_factors: List[Dict]) -> List[str]:
        """Generate recommendations based on triggered risk factors."""
        recommendations = []
        
        factor_recommendations = {
            'gpa': [
                'Meet with academic advisor to discuss study strategies',
                'Consider tutoring or study groups',
                'Review time management practices'
            ],
            'cgpa': [
                'Schedule appointment with academic advisor immediately',
                'Consider academic probation support services',
                'Evaluate course load for upcoming semester'
            ],
            'attendance': [
                'Improve class attendance immediately',
                'Contact professors about missed classes',
                'Review and address barriers to attendance'
            ],
            'course_failures': [
                'Schedule meeting with academic advisor',
                'Consider retaking failed courses',
                'Evaluate academic major fit'
            ],
            'gpa_trend': [
                'Identify causes of academic decline',
                'Seek academic support services',
                'Consider reducing course load'
            ],
            'missing_assessment': [
                'Complete all pending assessments immediately',
                'Contact instructors about makeup opportunities',
                'Review course requirements and deadlines'
            ]
        }
        
        for factor in risk_factors:
            category = factor['category']
            if category in factor_recommendations:
                recommendations.extend(factor_recommendations[category])
        
        return list(set(recommendations))  # Remove duplicates
    
    @classmethod
    @transaction.atomic
    def generate_warning_for_student(cls, student: Student, semester: Semester) -> Optional[EarlyWarningResult]:
        """
        Generate or update warning record for a student.
        Returns the created/updated EarlyWarningResult.
        """
        risk_data = cls.calculate_student_risk(student, semester)
        
        # Get or create warning result
        warning_result, created = EarlyWarningResult.objects.update_or_create(
            student=student,
            semester=semester,
            defaults={
                'risk_score': risk_data['total_score'],
                'warning_level': risk_data['warning_level'],
                'risk_factors': risk_data['risk_factors'],
                'recommendations': risk_data['recommendations'],
                'gpa_risk_score': risk_data['category_scores']['gpa'],
                'cgpa_risk_score': risk_data['category_scores']['cgpa'],
                'attendance_risk_score': risk_data['category_scores']['attendance'],
                'course_failure_risk_score': risk_data['category_scores']['course_failures'],
                'trend_risk_score': risk_data['category_scores']['trend'],
                'missing_assessment_risk_score': risk_data['category_scores']['missing_assessments'],
            }
        )
        
        return warning_result
    
    @classmethod
    def generate_warnings_for_semester(cls, semester: Semester) -> int:
        """
        Generate warnings for all students in a semester.
        Returns count of warnings generated.
        """
        # Get all students with enrollments in this semester
        from apps.students.models import Student
        
        students = Student.objects.filter(
            enrollments__course_offering__semester=semester
        ).distinct()
        
        count = 0
        for student in students:
            try:
                cls.generate_warning_for_student(student, semester)
                count += 1
            except Exception as e:
                # Log error but continue with other students
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error generating warning for student {student}: {e}")
        
        return count


def get_student_warning_summary(student: Student) -> Dict:
    """Get a summary of warnings for a student across all semesters."""
    warnings = EarlyWarningResult.objects.filter(
        student=student
    ).select_related('semester').order_by('-semester__start_date')
    
    return {
        'total_warnings': warnings.count(),
        'current_warning': warnings.filter(semester__is_active=True).first(),
        'warning_history': [
            {
                'semester': w.semester.name,
                'level': w.warning_level,
                'score': float(w.risk_score),
                'date': w.generated_at,
                'is_acknowledged': w.is_acknowledged
            }
            for w in warnings
        ],
        'at_risk_semesters': warnings.exclude(warning_level='green').count()
    }
