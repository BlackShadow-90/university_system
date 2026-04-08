"""
Academic Services Tests

Comprehensive test coverage for:
- GPA/CGPA calculations
- Attendance calculations
- Warning generation
- Grade mapping
- Enrollment logic
"""

from decimal import Decimal
from django.test import TestCase
from unittest.mock import Mock, MagicMock, patch
from apps.core.academic_services import (
    GradeScale,
    GPACalculationService,
    EarlyWarningCalculationService,
    AssessmentValidationService,
    FinalScoreCalculationService,
)


class GradeScaleTests(TestCase):
    """Test grade scale mapping functionality"""
    
    def setUp(self):
        self.grade_scale = GradeScale()
    
    def test_grade_a_plus_mapping(self):
        """Test A grade mapping (90-100%)"""
        grade, points = self.grade_scale.get_grade_for_percentage(Decimal('95'))
        self.assertEqual(grade, 'A')
        self.assertEqual(points, Decimal('4.0'))
    
    def test_grade_a_minus_mapping(self):
        """Test A- grade mapping (85-89%)"""
        grade, points = self.grade_scale.get_grade_for_percentage(Decimal('87'))
        self.assertEqual(grade, 'A-')
        self.assertEqual(points, Decimal('3.7'))
    
    def test_grade_b_plus_mapping(self):
        """Test B+ grade mapping (80-84%)"""
        grade, points = self.grade_scale.get_grade_for_percentage(Decimal('82'))
        self.assertEqual(grade, 'B+')
        self.assertEqual(points, Decimal('3.3'))
    
    def test_grade_b_mapping(self):
        """Test B grade mapping (75-79%)"""
        grade, points = self.grade_scale.get_grade_for_percentage(Decimal('77'))
        self.assertEqual(grade, 'B')
        self.assertEqual(points, Decimal('3.0'))
    
    def test_grade_b_minus_mapping(self):
        """Test B- grade mapping (70-74%)"""
        grade, points = self.grade_scale.get_grade_for_percentage(Decimal('72'))
        self.assertEqual(grade, 'B-')
        self.assertEqual(points, Decimal('2.7'))
    
    def test_grade_c_plus_mapping(self):
        """Test C+ grade mapping (65-69%)"""
        grade, points = self.grade_scale.get_grade_for_percentage(Decimal('67'))
        self.assertEqual(grade, 'C+')
        self.assertEqual(points, Decimal('2.3'))
    
    def test_grade_c_mapping(self):
        """Test C grade mapping (60-64%)"""
        grade, points = self.grade_scale.get_grade_for_percentage(Decimal('62'))
        self.assertEqual(grade, 'C')
        self.assertEqual(points, Decimal('2.0'))
    
    def test_grade_c_minus_mapping(self):
        """Test C- grade mapping (55-59%)"""
        grade, points = self.grade_scale.get_grade_for_percentage(Decimal('57'))
        self.assertEqual(grade, 'C-')
        self.assertEqual(points, Decimal('1.7'))
    
    def test_grade_d_mapping(self):
        """Test D grade mapping (50-54%)"""
        grade, points = self.grade_scale.get_grade_for_percentage(Decimal('52'))
        self.assertEqual(grade, 'D')
        self.assertEqual(points, Decimal('1.0'))
    
    def test_grade_f_mapping_high(self):
        """Test F grade mapping (0-49%) - high end"""
        grade, points = self.grade_scale.get_grade_for_percentage(Decimal('45'))
        self.assertEqual(grade, 'F')
        self.assertEqual(points, Decimal('0.0'))
    
    def test_grade_f_mapping_low(self):
        """Test F grade mapping (0-49%) - low end"""
        grade, points = self.grade_scale.get_grade_for_percentage(Decimal('0'))
        self.assertEqual(grade, 'F')
        self.assertEqual(points, Decimal('0.0'))
    
    def test_boundary_values(self):
        """Test grade boundaries"""
        # Test exact boundaries
        self.assertEqual(self.grade_scale.get_grade_for_percentage(Decimal('90'))[0], 'A')
        self.assertEqual(self.grade_scale.get_grade_for_percentage(Decimal('89'))[0], 'A-')
        self.assertEqual(self.grade_scale.get_grade_for_percentage(Decimal('85'))[0], 'A-')
        self.assertEqual(self.grade_scale.get_grade_for_percentage(Decimal('84'))[0], 'B+')
        self.assertEqual(self.grade_scale.get_grade_for_percentage(Decimal('80'))[0], 'B+')
        self.assertEqual(self.grade_scale.get_grade_for_percentage(Decimal('79'))[0], 'B')
        self.assertEqual(self.grade_scale.get_grade_for_percentage(Decimal('75'))[0], 'B')
        self.assertEqual(self.grade_scale.get_grade_for_percentage(Decimal('74'))[0], 'B-')
        self.assertEqual(self.grade_scale.get_grade_for_percentage(Decimal('70'))[0], 'B-')
        self.assertEqual(self.grade_scale.get_grade_for_percentage(Decimal('69'))[0], 'C+')
        self.assertEqual(self.grade_scale.get_grade_for_percentage(Decimal('65'))[0], 'C+')
        self.assertEqual(self.grade_scale.get_grade_for_percentage(Decimal('64'))[0], 'C')
        self.assertEqual(self.grade_scale.get_grade_for_percentage(Decimal('60'))[0], 'C')
        self.assertEqual(self.grade_scale.get_grade_for_percentage(Decimal('59'))[0], 'C-')
        self.assertEqual(self.grade_scale.get_grade_for_percentage(Decimal('55'))[0], 'C-')
        self.assertEqual(self.grade_scale.get_grade_for_percentage(Decimal('54'))[0], 'D')
        self.assertEqual(self.grade_scale.get_grade_for_percentage(Decimal('50'))[0], 'D')
        self.assertEqual(self.grade_scale.get_grade_for_percentage(Decimal('49'))[0], 'F')
    
    def test_custom_scale(self):
        """Test custom grade scale configuration"""
        custom_scale = [
            {'min': 80, 'max': 100, 'grade': 'A', 'points': Decimal('4.0')},
            {'min': 60, 'max': 79, 'grade': 'B', 'points': Decimal('3.0')},
            {'min': 0, 'max': 59, 'grade': 'F', 'points': Decimal('0.0')},
        ]
        custom_grade_scale = GradeScale(scale_config=custom_scale)
        
        grade, points = custom_grade_scale.get_grade_for_percentage(Decimal('85'))
        self.assertEqual(grade, 'A')
        
        grade, points = custom_grade_scale.get_grade_for_percentage(Decimal('70'))
        self.assertEqual(grade, 'B')
        
        grade, points = custom_grade_scale.get_grade_for_percentage(Decimal('50'))
        self.assertEqual(grade, 'F')


class GPACalculationServiceTests(TestCase):
    """Test GPA and CGPA calculation functionality"""
    
    def setUp(self):
        self.gpa_service = GPACalculationService()
    
    def test_get_grade_points(self):
        """Test grade point retrieval from final score"""
        # A grade (95%)
        points = self.gpa_service._get_grade_points(Decimal('95'))
        self.assertEqual(points, Decimal('4.0'))
        
        # B grade (77%)
        points = self.gpa_service._get_grade_points(Decimal('77'))
        self.assertEqual(points, Decimal('3.0'))
        
        # F grade (45%)
        points = self.gpa_service._get_grade_points(Decimal('45'))
        self.assertEqual(points, Decimal('0.0'))
    
    @patch('apps.core.academic_services.Enrollment')
    def test_calculate_semester_gpa_no_enrollments(self, mock_enrollment):
        """Test semester GPA calculation with no enrollments"""
        # Setup mock queryset that returns empty
        mock_queryset = MagicMock()
        mock_queryset.exists.return_value = False
        mock_enrollment.objects.filter.return_value = mock_queryset
        
        # Create mock student and semester
        mock_student = Mock()
        mock_semester = Mock()
        
        gpa, credits = self.gpa_service.calculate_semester_gpa(mock_student, mock_semester)
        
        self.assertEqual(gpa, Decimal('0.00'))
        self.assertEqual(credits, 0)
    
    @patch('apps.core.academic_services.Enrollment')
    def test_calculate_semester_gpa_single_course(self, mock_enrollment_class):
        """Test semester GPA calculation with single course"""
        # Create mock enrollment
        mock_course = Mock()
        mock_course.credit_hours = 3
        
        mock_course_offering = Mock()
        mock_course_offering.course = mock_course
        
        mock_enrollment = Mock()
        mock_enrollment.course_offering = mock_course_offering
        mock_enrollment.final_score = Decimal('85')  # A- = 3.7 points
        
        # Setup mock queryset
        mock_queryset = MagicMock()
        mock_queryset.exists.return_value = True
        mock_queryset.__iter__ = Mock(return_value=iter([mock_enrollment]))
        mock_enrollment_class.objects.filter.return_value.select_related.return_value = mock_queryset
        
        mock_student = Mock()
        mock_semester = Mock()
        
        # Patch the filter chain properly
        mock_enrollment_class.objects.filter.return_value.select_related.return_value = mock_queryset
        
        gpa, credits = self.gpa_service.calculate_semester_gpa(mock_student, mock_semester)
        
        # Expected: (3.7 * 3) / 3 = 3.7
        self.assertEqual(gpa, Decimal('3.70'))
        self.assertEqual(credits, 3)
    
    @patch('apps.core.academic_services.Enrollment')
    def test_calculate_semester_gpa_multiple_courses(self, mock_enrollment_class):
        """Test semester GPA calculation with multiple courses"""
        # Create mock enrollments
        enrollments = []
        
        # Course 1: 3 credits, 85% (A- = 3.7)
        course1 = Mock()
        course1.credit_hours = 3
        offering1 = Mock()
        offering1.course = course1
        enrollment1 = Mock()
        enrollment1.course_offering = offering1
        enrollment1.final_score = Decimal('85')
        enrollments.append(enrollment1)
        
        # Course 2: 4 credits, 77% (B = 3.0)
        course2 = Mock()
        course2.credit_hours = 4
        offering2 = Mock()
        offering2.course = course2
        enrollment2 = Mock()
        enrollment2.course_offering = offering2
        enrollment2.final_score = Decimal('77')
        enrollments.append(enrollment2)
        
        # Course 3: 3 credits, 92% (A = 4.0)
        course3 = Mock()
        course3.credit_hours = 3
        offering3 = Mock()
        offering3.course = course3
        enrollment3 = Mock()
        enrollment3.course_offering = offering3
        enrollment3.final_score = Decimal('92')
        enrollments.append(enrollment3)
        
        # Setup mock queryset
        mock_queryset = MagicMock()
        mock_queryset.exists.return_value = True
        mock_queryset.__iter__ = Mock(return_value=iter(enrollments))
        mock_enrollment_class.objects.filter.return_value.select_related.return_value = mock_queryset
        
        mock_student = Mock()
        mock_semester = Mock()
        
        gpa, credits = self.gpa_service.calculate_semester_gpa(mock_student, mock_semester)
        
        # Expected calculation:
        # Total points = (3.7 * 3) + (3.0 * 4) + (4.0 * 3) = 11.1 + 12.0 + 12.0 = 35.1
        # Total credits = 3 + 4 + 3 = 10
        # GPA = 35.1 / 10 = 3.51
        self.assertEqual(gpa, Decimal('3.51'))
        self.assertEqual(credits, 10)
    
    @patch('apps.core.academic_services.Enrollment')
    def test_calculate_semester_gpa_with_failing_grade(self, mock_enrollment_class):
        """Test semester GPA calculation with failing grade"""
        # Create mock enrollments
        enrollments = []
        
        # Course 1: 3 credits, 85% (A- = 3.7)
        course1 = Mock()
        course1.credit_hours = 3
        offering1 = Mock()
        offering1.course = course1
        enrollment1 = Mock()
        enrollment1.course_offering = offering1
        enrollment1.final_score = Decimal('85')
        enrollments.append(enrollment1)
        
        # Course 2: 3 credits, 45% (F = 0.0)
        course2 = Mock()
        course2.credit_hours = 3
        offering2 = Mock()
        offering2.course = course2
        enrollment2 = Mock()
        enrollment2.course_offering = offering2
        enrollment2.final_score = Decimal('45')
        enrollments.append(enrollment2)
        
        # Setup mock queryset
        mock_queryset = MagicMock()
        mock_queryset.exists.return_value = True
        mock_queryset.__iter__ = Mock(return_value=iter(enrollments))
        mock_enrollment_class.objects.filter.return_value.select_related.return_value = mock_queryset
        
        mock_student = Mock()
        mock_semester = Mock()
        
        gpa, credits = self.gpa_service.calculate_semester_gpa(mock_student, mock_semester)
        
        # Expected calculation:
        # Total points = (3.7 * 3) + (0.0 * 3) = 11.1 + 0 = 11.1
        # Total credits = 3 + 3 = 6
        # GPA = 11.1 / 6 = 1.85
        self.assertEqual(gpa, Decimal('1.85'))
        self.assertEqual(credits, 6)
    
    @patch('apps.core.academic_services.Enrollment')
    def test_calculate_cgpa_no_enrollments(self, mock_enrollment_class):
        """Test CGPA calculation with no enrollments"""
        # Setup mock queryset that returns empty
        mock_queryset = MagicMock()
        mock_queryset.__iter__ = Mock(return_value=iter([]))
        mock_enrollment_class.objects.filter.return_value.select_related.return_value = mock_queryset
        
        mock_student = Mock()
        
        cgpa, credits = self.gpa_service.calculate_cgpa(mock_student)
        
        self.assertEqual(cgpa, Decimal('0.00'))
        self.assertEqual(credits, 0)
    
    @patch('apps.core.academic_services.Enrollment')
    def test_calculate_cgpa_single_semester(self, mock_enrollment_class):
        """Test CGPA calculation with single semester"""
        # Create mock enrollments
        enrollments = []
        
        # Course 1: 3 credits, 85% (A- = 3.7)
        course1 = Mock()
        course1.credit_hours = 3
        course1.id = 1
        offering1 = Mock()
        offering1.course = course1
        enrollment1 = Mock()
        enrollment1.course_offering = offering1
        enrollment1.final_score = Decimal('85')
        enrollments.append(enrollment1)
        
        # Setup mock queryset
        mock_queryset = MagicMock()
        mock_queryset.__iter__ = Mock(return_value=iter(enrollments))
        mock_enrollment_class.objects.filter.return_value.select_related.return_value = mock_queryset
        
        mock_student = Mock()
        
        cgpa, credits = self.gpa_service.calculate_cgpa(mock_student)
        
        # Expected: (3.7 * 3) / 3 = 3.7
        self.assertEqual(cgpa, Decimal('3.70'))
        self.assertEqual(credits, 3)
    
    @patch('apps.core.academic_services.Enrollment')
    def test_calculate_cgpa_repeated_course_keep_best_grade(self, mock_enrollment_class):
        """Test CGPA calculation with repeated course - keeps best grade"""
        # Create mock enrollments - same course taken twice
        enrollments = []
        
        # First attempt: 3 credits, 65% (C+ = 2.3) - FAILED
        course1 = Mock()
        course1.credit_hours = 3
        course1.id = 1  # Same course ID
        offering1 = Mock()
        offering1.course = course1
        enrollment1 = Mock()
        enrollment1.course_offering = offering1
        enrollment1.final_score = Decimal('65')  # C+ = 2.3
        enrollments.append(enrollment1)
        
        # Second attempt: 3 credits, 85% (A- = 3.7) - PASSED (better grade)
        course2 = Mock()
        course2.credit_hours = 3
        course2.id = 1  # Same course ID
        offering2 = Mock()
        offering2.course = course2
        enrollment2 = Mock()
        enrollment2.course_offering = offering2
        enrollment2.final_score = Decimal('85')  # A- = 3.7
        enrollments.append(enrollment2)
        
        # Setup mock queryset
        mock_queryset = MagicMock()
        mock_queryset.__iter__ = Mock(return_value=iter(enrollments))
        mock_enrollment_class.objects.filter.return_value.select_related.return_value = mock_queryset
        
        mock_student = Mock()
        
        cgpa, credits = self.gpa_service.calculate_cgpa(mock_student)
        
        # Expected: Should use best grade (3.7) not sum of both
        # Points = 3.7 * 3 = 11.1
        # Credits = 3
        # CGPA = 11.1 / 3 = 3.7
        self.assertEqual(cgpa, Decimal('3.70'))
        self.assertEqual(credits, 3)  # Should only count credits once
    
    @patch('apps.core.academic_services.Enrollment')
    def test_calculate_cgpa_multiple_semesters(self, mock_enrollment_class):
        """Test CGPA calculation across multiple semesters"""
        # Create mock enrollments
        enrollments = []
        
        # Semester 1: 2 courses
        # Course 1: 3 credits, 85% (A- = 3.7)
        course1 = Mock()
        course1.credit_hours = 3
        course1.id = 1
        offering1 = Mock()
        offering1.course = course1
        enrollment1 = Mock()
        enrollment1.course_offering = offering1
        enrollment1.final_score = Decimal('85')
        enrollments.append(enrollment1)
        
        # Course 2: 4 credits, 77% (B = 3.0)
        course2 = Mock()
        course2.credit_hours = 4
        course2.id = 2
        offering2 = Mock()
        offering2.course = course2
        enrollment2 = Mock()
        enrollment2.course_offering = offering2
        enrollment2.final_score = Decimal('77')
        enrollments.append(enrollment2)
        
        # Setup mock queryset
        mock_queryset = MagicMock()
        mock_queryset.__iter__ = Mock(return_value=iter(enrollments))
        mock_enrollment_class.objects.filter.return_value.select_related.return_value = mock_queryset
        
        mock_student = Mock()
        
        cgpa, credits = self.gpa_service.calculate_cgpa(mock_student)
        
        # Expected:
        # Points = (3.7 * 3) + (3.0 * 4) = 11.1 + 12.0 = 23.1
        # Credits = 3 + 4 = 7
        # CGPA = 23.1 / 7 = 3.30
        self.assertEqual(cgpa, Decimal('3.30'))
        self.assertEqual(credits, 7)


class AttendanceCalculationTests(TestCase):
    """Test attendance risk calculation functionality"""
    
    def test_attendance_risk_perfect(self):
        """Test attendance risk with 100% attendance"""
        mock_enrollment = Mock()
        mock_enrollment.attendance_percentage = Decimal('100')
        
        risk = EarlyWarningCalculationService.calculate_attendance_risk(mock_enrollment)
        self.assertEqual(risk, Decimal('0'))
    
    def test_attendance_risk_excellent(self):
        """Test attendance risk with 85% attendance"""
        mock_enrollment = Mock()
        mock_enrollment.attendance_percentage = Decimal('85')
        
        risk = EarlyWarningCalculationService.calculate_attendance_risk(mock_enrollment)
        self.assertEqual(risk, Decimal('0'))
    
    def test_attendance_risk_good(self):
        """Test attendance risk with 80% attendance (boundary)"""
        mock_enrollment = Mock()
        mock_enrollment.attendance_percentage = Decimal('80')
        
        risk = EarlyWarningCalculationService.calculate_attendance_risk(mock_enrollment)
        self.assertEqual(risk, Decimal('0'))
    
    def test_attendance_risk_moderate_high(self):
        """Test attendance risk with 75% attendance"""
        mock_enrollment = Mock()
        mock_enrollment.attendance_percentage = Decimal('75')
        
        risk = EarlyWarningCalculationService.calculate_attendance_risk(mock_enrollment)
        self.assertEqual(risk, Decimal('25'))
    
    def test_attendance_risk_moderate_low(self):
        """Test attendance risk with 70% attendance (boundary)"""
        mock_enrollment = Mock()
        mock_enrollment.attendance_percentage = Decimal('70')
        
        risk = EarlyWarningCalculationService.calculate_attendance_risk(mock_enrollment)
        self.assertEqual(risk, Decimal('25'))
    
    def test_attendance_risk_concerning_high(self):
        """Test attendance risk with 65% attendance"""
        mock_enrollment = Mock()
        mock_enrollment.attendance_percentage = Decimal('65')
        
        risk = EarlyWarningCalculationService.calculate_attendance_risk(mock_enrollment)
        self.assertEqual(risk, Decimal('50'))
    
    def test_attendance_risk_concerning_low(self):
        """Test attendance risk with 60% attendance (boundary)"""
        mock_enrollment = Mock()
        mock_enrollment.attendance_percentage = Decimal('60')
        
        risk = EarlyWarningCalculationService.calculate_attendance_risk(mock_enrollment)
        self.assertEqual(risk, Decimal('50'))
    
    def test_attendance_risk_high_risk_high(self):
        """Test attendance risk with 55% attendance"""
        mock_enrollment = Mock()
        mock_enrollment.attendance_percentage = Decimal('55')
        
        risk = EarlyWarningCalculationService.calculate_attendance_risk(mock_enrollment)
        self.assertEqual(risk, Decimal('75'))
    
    def test_attendance_risk_high_risk_low(self):
        """Test attendance risk with 50% attendance (boundary)"""
        mock_enrollment = Mock()
        mock_enrollment.attendance_percentage = Decimal('50')
        
        risk = EarlyWarningCalculationService.calculate_attendance_risk(mock_enrollment)
        self.assertEqual(risk, Decimal('75'))
    
    def test_attendance_risk_critical(self):
        """Test attendance risk with 45% attendance"""
        mock_enrollment = Mock()
        mock_enrollment.attendance_percentage = Decimal('45')
        
        risk = EarlyWarningCalculationService.calculate_attendance_risk(mock_enrollment)
        self.assertEqual(risk, Decimal('100'))
    
    def test_attendance_risk_none(self):
        """Test attendance risk with None value"""
        mock_enrollment = Mock()
        mock_enrollment.attendance_percentage = None
        
        risk = EarlyWarningCalculationService.calculate_attendance_risk(mock_enrollment)
        self.assertEqual(risk, Decimal('100'))
    
    def test_attendance_risk_zero(self):
        """Test attendance risk with 0% attendance"""
        mock_enrollment = Mock()
        mock_enrollment.attendance_percentage = Decimal('0')
        
        risk = EarlyWarningCalculationService.calculate_attendance_risk(mock_enrollment)
        self.assertEqual(risk, Decimal('100'))


class AcademicRiskCalculationTests(TestCase):
    """Test academic risk calculation functionality"""
    
    def test_academic_risk_perfect_score(self):
        """Test academic risk with 100% score"""
        mock_enrollment = Mock()
        mock_enrollment.final_score = Decimal('100')
        
        risk = EarlyWarningCalculationService.calculate_academic_risk(mock_enrollment)
        self.assertEqual(risk, Decimal('0'))
    
    def test_academic_risk_excellent(self):
        """Test academic risk with 75% score"""
        mock_enrollment = Mock()
        mock_enrollment.final_score = Decimal('75')
        
        risk = EarlyWarningCalculationService.calculate_academic_risk(mock_enrollment)
        self.assertEqual(risk, Decimal('0'))
    
    def test_academic_risk_good_boundary(self):
        """Test academic risk with 70% score (boundary)"""
        mock_enrollment = Mock()
        mock_enrollment.final_score = Decimal('70')
        
        risk = EarlyWarningCalculationService.calculate_academic_risk(mock_enrollment)
        self.assertEqual(risk, Decimal('0'))
    
    def test_academic_risk_moderate_high(self):
        """Test academic risk with 65% score"""
        mock_enrollment = Mock()
        mock_enrollment.final_score = Decimal('65')
        
        risk = EarlyWarningCalculationService.calculate_academic_risk(mock_enrollment)
        self.assertEqual(risk, Decimal('25'))
    
    def test_academic_risk_moderate_low(self):
        """Test academic risk with 60% score (boundary)"""
        mock_enrollment = Mock()
        mock_enrollment.final_score = Decimal('60')
        
        risk = EarlyWarningCalculationService.calculate_academic_risk(mock_enrollment)
        self.assertEqual(risk, Decimal('25'))
    
    def test_academic_risk_concerning_high(self):
        """Test academic risk with 55% score"""
        mock_enrollment = Mock()
        mock_enrollment.final_score = Decimal('55')
        
        risk = EarlyWarningCalculationService.calculate_academic_risk(mock_enrollment)
        self.assertEqual(risk, Decimal('50'))
    
    def test_academic_risk_concerning_low(self):
        """Test academic risk with 50% score (boundary)"""
        mock_enrollment = Mock()
        mock_enrollment.final_score = Decimal('50')
        
        risk = EarlyWarningCalculationService.calculate_academic_risk(mock_enrollment)
        self.assertEqual(risk, Decimal('50'))
    
    def test_academic_risk_high_risk_high(self):
        """Test academic risk with 45% score"""
        mock_enrollment = Mock()
        mock_enrollment.final_score = Decimal('45')
        
        risk = EarlyWarningCalculationService.calculate_academic_risk(mock_enrollment)
        self.assertEqual(risk, Decimal('75'))
    
    def test_academic_risk_high_risk_low(self):
        """Test academic risk with 40% score (boundary)"""
        mock_enrollment = Mock()
        mock_enrollment.final_score = Decimal('40')
        
        risk = EarlyWarningCalculationService.calculate_academic_risk(mock_enrollment)
        self.assertEqual(risk, Decimal('75'))
    
    def test_academic_risk_critical(self):
        """Test academic risk with 35% score"""
        mock_enrollment = Mock()
        mock_enrollment.final_score = Decimal('35')
        
        risk = EarlyWarningCalculationService.calculate_academic_risk(mock_enrollment)
        self.assertEqual(risk, Decimal('100'))
    
    def test_academic_risk_zero(self):
        """Test academic risk with 0% score"""
        mock_enrollment = Mock()
        mock_enrollment.final_score = Decimal('0')
        
        risk = EarlyWarningCalculationService.calculate_academic_risk(mock_enrollment)
        self.assertEqual(risk, Decimal('100'))
    
    @patch('apps.core.academic_services.FinalScoreCalculationService')
    def test_academic_risk_no_final_score(self, mock_final_service):
        """Test academic risk calculation when final_score is None"""
        mock_enrollment = Mock()
        mock_enrollment.final_score = None
        mock_final_service.calculate_weighted_score.return_value = Decimal('65')
        
        risk = EarlyWarningCalculationService.calculate_academic_risk(mock_enrollment)
        
        # Should use calculated preliminary score
        mock_final_service.calculate_weighted_score.assert_called_once_with(mock_enrollment)
        self.assertEqual(risk, Decimal('25'))  # 65% falls in moderate range


class WarningLevelTests(TestCase):
    """Test warning level determination"""
    
    def test_warning_level_green(self):
        """Test green warning level (low risk)"""
        level = EarlyWarningCalculationService.determine_warning_level(
            Decimal('0'), Decimal('0')
        )
        self.assertEqual(level, 'green')
    
    def test_warning_level_green_boundary(self):
        """Test green warning level at boundary (24%)"""
        level = EarlyWarningCalculationService.determine_warning_level(
            Decimal('24'), Decimal('10')
        )
        self.assertEqual(level, 'green')
    
    def test_warning_level_yellow_low(self):
        """Test yellow warning level at lower boundary (25%)"""
        level = EarlyWarningCalculationService.determine_warning_level(
            Decimal('25'), Decimal('10')
        )
        self.assertEqual(level, 'yellow')
    
    def test_warning_level_yellow_mid(self):
        """Test yellow warning level (moderate risk)"""
        level = EarlyWarningCalculationService.determine_warning_level(
            Decimal('40'), Decimal('30')
        )
        self.assertEqual(level, 'yellow')
    
    def test_warning_level_yellow_high(self):
        """Test yellow warning level at upper boundary (49%)"""
        level = EarlyWarningCalculationService.determine_warning_level(
            Decimal('49'), Decimal('20')
        )
        self.assertEqual(level, 'yellow')
    
    def test_warning_level_orange_low(self):
        """Test orange warning level at lower boundary (50%)"""
        level = EarlyWarningCalculationService.determine_warning_level(
            Decimal('50'), Decimal('30')
        )
        self.assertEqual(level, 'orange')
    
    def test_warning_level_orange_mid(self):
        """Test orange warning level (high risk)"""
        level = EarlyWarningCalculationService.determine_warning_level(
            Decimal('60'), Decimal('55')
        )
        self.assertEqual(level, 'orange')
    
    def test_warning_level_orange_high(self):
        """Test orange warning level at upper boundary (74%)"""
        level = EarlyWarningCalculationService.determine_warning_level(
            Decimal('74'), Decimal('50')
        )
        self.assertEqual(level, 'orange')
    
    def test_warning_level_red_boundary(self):
        """Test red warning level at boundary (75%)"""
        level = EarlyWarningCalculationService.determine_warning_level(
            Decimal('75'), Decimal('50')
        )
        self.assertEqual(level, 'red')
    
    def test_warning_level_red(self):
        """Test red warning level (critical risk)"""
        level = EarlyWarningCalculationService.determine_warning_level(
            Decimal('100'), Decimal('90')
        )
        self.assertEqual(level, 'red')
    
    def test_warning_level_uses_max_risk(self):
        """Test that warning level uses the higher of two risk scores"""
        # High attendance risk, low academic risk
        level = EarlyWarningCalculationService.determine_warning_level(
            Decimal('80'), Decimal('20')
        )
        self.assertEqual(level, 'red')
        
        # Low attendance risk, high academic risk
        level = EarlyWarningCalculationService.determine_warning_level(
            Decimal('20'), Decimal('80')
        )
        self.assertEqual(level, 'red')


class AssessmentValidationTests(TestCase):
    """Test assessment validation functionality"""
    
    @patch('apps.core.academic_services.AssessmentComponent')
    def test_validate_component_weights_valid(self, mock_component_class):
        """Test validation with correct 100% total weight"""
        # Setup mock queryset
        mock_queryset = MagicMock()
        mock_queryset.aggregate.return_value = {'total': Decimal('100')}
        mock_component_class.objects.filter.return_value = mock_queryset
        
        mock_offering = Mock()
        is_valid, error = AssessmentValidationService.validate_component_weights(mock_offering)
        
        self.assertTrue(is_valid)
        self.assertEqual(error, "")
    
    @patch('apps.core.academic_services.AssessmentComponent')
    def test_validate_component_weights_under(self, mock_component_class):
        """Test validation with under 100% total weight"""
        # Setup mock queryset
        mock_queryset = MagicMock()
        mock_queryset.aggregate.return_value = {'total': Decimal('80')}
        mock_component_class.objects.filter.return_value = mock_queryset
        
        mock_offering = Mock()
        is_valid, error = AssessmentValidationService.validate_component_weights(mock_offering)
        
        self.assertFalse(is_valid)
        self.assertIn("Total weight must be 100%", error)
        self.assertIn("80%", error)
    
    @patch('apps.core.academic_services.AssessmentComponent')
    def test_validate_component_weights_over(self, mock_component_class):
        """Test validation with over 100% total weight"""
        # Setup mock queryset
        mock_queryset = MagicMock()
        mock_queryset.aggregate.return_value = {'total': Decimal('120')}
        mock_component_class.objects.filter.return_value = mock_queryset
        
        mock_offering = Mock()
        is_valid, error = AssessmentValidationService.validate_component_weights(mock_offering)
        
        self.assertFalse(is_valid)
        self.assertIn("Total weight must be 100%", error)
        self.assertIn("120%", error)
    
    @patch('apps.core.academic_services.AssessmentComponent')
    def test_validate_component_weights_no_components(self, mock_component_class):
        """Test validation with no components (0% total weight)"""
        # Setup mock queryset
        mock_queryset = MagicMock()
        mock_queryset.aggregate.return_value = {'total': None}
        mock_component_class.objects.filter.return_value = mock_queryset
        
        mock_offering = Mock()
        is_valid, error = AssessmentValidationService.validate_component_weights(mock_offering)
        
        self.assertFalse(is_valid)
        self.assertIn("Total weight must be 100%", error)
    
    def test_validate_score_valid(self):
        """Test score validation with valid score"""
        mock_component = Mock()
        mock_component.max_score = Decimal('100')
        
        is_valid, error = AssessmentValidationService.validate_score(mock_component, 85.5)
        
        self.assertTrue(is_valid)
        self.assertEqual(error, "")
    
    def test_validate_score_negative(self):
        """Test score validation with negative score"""
        mock_component = Mock()
        mock_component.max_score = Decimal('100')
        
        is_valid, error = AssessmentValidationService.validate_score(mock_component, -5)
        
        self.assertFalse(is_valid)
        self.assertEqual(error, "Score cannot be negative")
    
    def test_validate_score_exceeds_max(self):
        """Test score validation with score exceeding maximum"""
        mock_component = Mock()
        mock_component.max_score = Decimal('100')
        
        is_valid, error = AssessmentValidationService.validate_score(mock_component, 105)
        
        self.assertFalse(is_valid)
        self.assertIn("Score cannot exceed maximum", error)
    
    def test_validate_score_at_max(self):
        """Test score validation with score at maximum (boundary)"""
        mock_component = Mock()
        mock_component.max_score = Decimal('100')
        
        is_valid, error = AssessmentValidationService.validate_score(mock_component, 100)
        
        self.assertTrue(is_valid)
        self.assertEqual(error, "")
    
    def test_validate_score_zero(self):
        """Test score validation with zero score"""
        mock_component = Mock()
        mock_component.max_score = Decimal('100')
        
        is_valid, error = AssessmentValidationService.validate_score(mock_component, 0)
        
        self.assertTrue(is_valid)
        self.assertEqual(error, "")


class FinalScoreCalculationTests(TestCase):
    """Test final score calculation functionality"""
    
    @patch('apps.core.academic_services.AssessmentScore')
    @patch('apps.core.academic_services.AssessmentComponent')
    def test_calculate_weighted_score_no_components(self, mock_component_class, mock_score_class):
        """Test weighted score calculation with no components"""
        # Setup mock queryset with no components
        mock_queryset = MagicMock()
        mock_queryset.exists.return_value = False
        mock_component_class.objects.filter.return_value = mock_queryset
        
        mock_enrollment = Mock()
        score = FinalScoreCalculationService.calculate_weighted_score(mock_enrollment)
        
        self.assertEqual(score, Decimal('0'))
    
    @patch('apps.core.academic_services.AssessmentScore')
    @patch('apps.core.academic_services.AssessmentComponent')
    def test_calculate_weighted_score_single_component(self, mock_component_class, mock_score_class):
        """Test weighted score calculation with single component"""
        # Create mock component
        mock_component = Mock()
        mock_component.pk = 1
        mock_component.max_score = Decimal('100')
        mock_component.weight_percentage = Decimal('100')
        
        # Setup component queryset
        mock_component_queryset = MagicMock()
        mock_component_queryset.exists.return_value = True
        mock_component_queryset.__iter__ = Mock(return_value=iter([mock_component]))
        mock_component_class.objects.filter.return_value = mock_component_queryset
        
        # Create mock score
        mock_score = Mock()
        mock_score.assessment_component_id = 1
        mock_score.score = 85
        
        # Setup score queryset
        mock_score_queryset = MagicMock()
        mock_score_queryset.__iter__ = Mock(return_value=iter([mock_score]))
        mock_score_class.objects.filter.return_value.select_related.return_value = mock_score_queryset
        
        mock_enrollment = Mock()
        score = FinalScoreCalculationService.calculate_weighted_score(mock_enrollment)
        
        # Expected: (85/100 * 100) = 85.00
        self.assertEqual(score, Decimal('85.00'))
    
    @patch('apps.core.academic_services.AssessmentScore')
    @patch('apps.core.academic_services.AssessmentComponent')
    def test_calculate_weighted_score_multiple_components(self, mock_component_class, mock_score_class):
        """Test weighted score calculation with multiple components"""
        # Create mock components
        component1 = Mock()
        component1.pk = 1
        component1.max_score = Decimal('100')
        component1.weight_percentage = Decimal('40')
        
        component2 = Mock()
        component2.pk = 2
        component2.max_score = Decimal('100')
        component2.weight_percentage = Decimal('60')
        
        # Setup component queryset
        mock_component_queryset = MagicMock()
        mock_component_queryset.exists.return_value = True
        mock_component_queryset.__iter__ = Mock(return_value=iter([component1, component2]))
        mock_component_class.objects.filter.return_value = mock_component_queryset
        
        # Create mock scores
        score1 = Mock()
        score1.assessment_component_id = 1
        score1.score = 80  # (80/100 * 40) = 32
        
        score2 = Mock()
        score2.assessment_component_id = 2
        score2.score = 90  # (90/100 * 60) = 54
        
        # Setup score queryset
        mock_score_queryset = MagicMock()
        mock_score_queryset.__iter__ = Mock(return_value=iter([score1, score2]))
        mock_score_class.objects.filter.return_value.select_related.return_value = mock_score_queryset
        
        mock_enrollment = Mock()
        score = FinalScoreCalculationService.calculate_weighted_score(mock_enrollment)
        
        # Expected: 32 + 54 = 86.00
        self.assertEqual(score, Decimal('86.00'))
    
    @patch('apps.core.academic_services.AssessmentScore')
    @patch('apps.core.academic_services.AssessmentComponent')
    def test_calculate_weighted_score_missing_score(self, mock_component_class, mock_score_class):
        """Test weighted score calculation with missing score for a component"""
        # Create mock components
        component1 = Mock()
        component1.pk = 1
        component1.max_score = Decimal('100')
        component1.weight_percentage = Decimal('50')
        
        component2 = Mock()
        component2.pk = 2
        component2.max_score = Decimal('100')
        component2.weight_percentage = Decimal('50')
        
        # Setup component queryset
        mock_component_queryset = MagicMock()
        mock_component_queryset.exists.return_value = True
        mock_component_queryset.__iter__ = Mock(return_value=iter([component1, component2]))
        mock_component_class.objects.filter.return_value = mock_component_queryset
        
        # Only one score (missing score for component 2)
        score1 = Mock()
        score1.assessment_component_id = 1
        score1.score = 80  # (80/100 * 50) = 40
        
        # Setup score queryset
        mock_score_queryset = MagicMock()
        mock_score_queryset.__iter__ = Mock(return_value=iter([score1]))
        mock_score_class.objects.filter.return_value.select_related.return_value = mock_score_queryset
        
        mock_enrollment = Mock()
        score = FinalScoreCalculationService.calculate_weighted_score(mock_enrollment)
        
        # Expected: 40 (component 2 contributes 0)
        self.assertEqual(score, Decimal('40.00'))
    
    @patch('apps.core.academic_services.AssessmentScore')
    @patch('apps.core.academic_services.AssessmentComponent')
    def test_calculate_weighted_score_none_score(self, mock_component_class, mock_score_class):
        """Test weighted score calculation with None score"""
        # Create mock component
        mock_component = Mock()
        mock_component.pk = 1
        mock_component.max_score = Decimal('100')
        mock_component.weight_percentage = Decimal('100')
        
        # Setup component queryset
        mock_component_queryset = MagicMock()
        mock_component_queryset.exists.return_value = True
        mock_component_queryset.__iter__ = Mock(return_value=iter([mock_component]))
        mock_component_class.objects.filter.return_value = mock_component_queryset
        
        # Create mock score with None value
        mock_score = Mock()
        mock_score.assessment_component_id = 1
        mock_score.score = None
        
        # Setup score queryset
        mock_score_queryset = MagicMock()
        mock_score_queryset.__iter__ = Mock(return_value=iter([mock_score]))
        mock_score_class.objects.filter.return_value.select_related.return_value = mock_score_queryset
        
        mock_enrollment = Mock()
        score = FinalScoreCalculationService.calculate_weighted_score(mock_enrollment)
        
        # Expected: 0 (None score contributes 0)
        self.assertEqual(score, Decimal('0.00'))
    
    @patch('apps.core.academic_services.FinalScoreCalculationService.calculate_weighted_score')
    def test_update_final_score(self, mock_calculate):
        """Test updating final score on enrollment"""
        mock_calculate.return_value = Decimal('85.50')
        
        mock_enrollment = Mock()
        mock_enrollment.save = Mock()
        
        FinalScoreCalculationService.update_final_score(mock_enrollment)
        
        self.assertEqual(mock_enrollment.final_score, Decimal('85.50'))
        mock_enrollment.save.assert_called_once_with(update_fields=['final_score'])
