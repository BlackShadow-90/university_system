"""
Attendance Service Layer

Centralized service for all attendance-related operations including:
- Attendance recording and validation
- Attendance percentage calculation
- Low attendance detection
- Integration with warning system
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Tuple
from datetime import date, timedelta
from django.db import transaction
from django.db.models import Count, Q
from django.conf import settings
from django.utils import timezone


class AttendanceCalculationService:
    """
    Service for calculating attendance statistics.
    """
    
    @staticmethod
    def calculate_attendance_percentage(enrollment) -> Decimal:
        """
        Calculate attendance percentage for an enrollment.
        
        Formula: attendance_percentage = present_classes / total_classes × 100
        
        Args:
            enrollment: Enrollment instance
            
        Returns:
            Attendance percentage as Decimal
        """
        if enrollment.total_classes == 0:
            return Decimal('100.00')  # Default to 100% if no classes held
        
        percentage = (
            Decimal(str(enrollment.attended_classes)) / 
            Decimal(str(enrollment.total_classes)) * 100
        )
        
        return percentage.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @staticmethod
    def get_attendance_summary(enrollment) -> Dict:
        """
        Get comprehensive attendance summary for an enrollment.
        
        Args:
            enrollment: Enrollment instance
            
        Returns:
            Dictionary with attendance statistics
        """
        from apps.attendance.models import AttendanceRecord
        
        records = AttendanceRecord.objects.filter(enrollment=enrollment)
        
        summary = {
            'total_classes': enrollment.total_classes,
            'attended_classes': enrollment.attended_classes,
            'percentage': enrollment.attendance_percentage or Decimal('0'),
            'status_breakdown': {
                'present': records.filter(status='present').count(),
                'absent': records.filter(status='absent').count(),
                'late': records.filter(status='late').count(),
                'excused': records.filter(status='excused').count(),
                'medical': records.filter(status='medical').count(),
                'official': records.filter(status='official').count(),
            }
        }
        
        return summary


class AttendanceThresholdService:
    """
    Service for checking attendance against thresholds.
    """
    
    DEFAULT_THRESHOLD = 75  # Default minimum attendance percentage
    
    @classmethod
    def get_threshold(cls) -> int:
        """
        Get the current attendance threshold from settings.
        
        Returns:
            Minimum attendance percentage required
        """
        return getattr(settings, 'ATTENDANCE_THRESHOLD', cls.DEFAULT_THRESHOLD)
    
    @classmethod
    def is_low_attendance(cls, enrollment) -> bool:
        """
        Check if enrollment has low attendance.
        
        Args:
            enrollment: Enrollment instance
            
        Returns:
            True if attendance is below threshold
        """
        percentage = enrollment.attendance_percentage
        
        if percentage is None:
            return False
        
        threshold = cls.get_threshold()
        return float(percentage) < threshold
    
    @classmethod
    def get_attendance_status(cls, enrollment) -> str:
        """
        Get attendance status label for an enrollment.
        
        Args:
            enrollment: Enrollment instance
            
        Returns:
            Status string: 'good', 'warning', or 'critical'
        """
        percentage = enrollment.attendance_percentage
        
        if percentage is None:
            return 'unknown'
        
        threshold = cls.get_threshold()
        pct = float(percentage)
        
        if pct >= threshold:
            return 'good'
        elif pct >= threshold - 10:  # Within 10% of threshold
            return 'warning'
        else:
            return 'critical'


class AttendanceRecordingService:
    """
    Service for recording and managing attendance.
    """
    
    @staticmethod
    def can_record_attendance(course_offering, attendance_date: date) -> Tuple[bool, str]:
        """
        Check if attendance can be recorded for a date.
        
        Args:
            course_offering: CourseOffering instance
            attendance_date: Date to check
            
        Returns:
            Tuple of (can_record, error_message)
        """
        today = timezone.now().date()
        
        # Cannot record future dates
        if attendance_date > today:
            return False, "Cannot mark attendance for future dates"
        
        # Check if date is within course offering period
        semester = course_offering.semester
        if attendance_date < semester.start_date:
            return False, "Date is before semester start"
        if attendance_date > semester.end_date:
            return False, "Date is after semester end"
        
        return True, ""
    
    @staticmethod
    @transaction.atomic
    def bulk_record_attendance(
        course_offering,
        attendance_date: date,
        attendance_data: Dict[int, str],  # enrollment_id -> status
        recorded_by,
        remarks: Optional[Dict[int, str]] = None
    ) -> Dict:
        """
        Record attendance for multiple students at once.
        
        Args:
            course_offering: CourseOffering instance
            attendance_date: Date of attendance
            attendance_data: Dictionary mapping enrollment IDs to status
            recorded_by: User recording the attendance
            remarks: Optional dictionary of remarks per enrollment
            
        Returns:
            Dictionary with recording results
        """
        from apps.attendance.models import AttendanceRecord
        from apps.enrollments.models import Enrollment
        
        can_record, error = AttendanceRecordingService.can_record_attendance(
            course_offering, attendance_date
        )
        
        if not can_record:
            return {'success': False, 'error': error}
        
        records_created = 0
        records_updated = 0
        errors = []
        
        for enrollment_id, status in attendance_data.items():
            try:
                enrollment = Enrollment.objects.get(
                    pk=enrollment_id,
                    course_offering=course_offering
                )
                
                remark = remarks.get(enrollment_id, '') if remarks else ''
                
                record, created = AttendanceRecord.objects.update_or_create(
                    enrollment=enrollment,
                    attendance_date=attendance_date,
                    defaults={
                        'status': status,
                        'remarks': remark,
                        'recorded_by': recorded_by
                    }
                )
                
                if created:
                    records_created += 1
                else:
                    records_updated += 1
                    
            except Enrollment.DoesNotExist:
                errors.append(f"Enrollment {enrollment_id} not found")
            except Exception as e:
                errors.append(f"Error for enrollment {enrollment_id}: {str(e)}")
        
        return {
            'success': True,
            'records_created': records_created,
            'records_updated': records_updated,
            'errors': errors
        }
    
    @staticmethod
    def get_class_sessions(course_offering, start_date: date, end_date: date) -> List[date]:
        """
        Get list of class session dates within a range.
        
        Args:
            course_offering: CourseOffering instance
            start_date: Start of range
            end_date: End of range
            
        Returns:
            List of dates when classes were/should be held
        """
        # Parse schedule to get days of week
        schedule = course_offering.schedule
        if not schedule:
            return []
        
        # This is a simplified version - could be enhanced with more complex scheduling
        import re
        day_map = {
            'mon': 0, 'monday': 0,
            'tue': 1, 'tuesday': 1,
            'wed': 2, 'wednesday': 2,
            'thu': 3, 'thursday': 3,
            'fri': 4, 'friday': 4,
            'sat': 5, 'saturday': 5,
            'sun': 6, 'sunday': 6,
        }
        
        # Extract days from schedule string
        schedule_lower = schedule.lower()
        class_days = []
        for day_name, day_num in day_map.items():
            if day_name in schedule_lower:
                class_days.append(day_num)
        
        class_days = sorted(set(class_days))
        if not class_days:
            # If no days parsed, default to all weekdays
            class_days = [0, 1, 2, 3, 4]
        
        # Generate dates
        sessions = []
        current = start_date
        
        while current <= end_date:
            if current.weekday() in class_days:
                sessions.append(current)
            current += timedelta(days=1)
        
        return sessions


class AttendanceWarningIntegrationService:
    """
    Service for integrating attendance with warning system.
    """
    
    @staticmethod
    def update_low_attendance_warnings(enrollment) -> None:
        """
        Update warning status based on attendance.
        
        Args:
            enrollment: Enrollment instance
        """
        from apps.warnings.models import EarlyWarningResult
        
        is_low = AttendanceThresholdService.is_low_attendance(enrollment)
        
        if is_low:
            # Get or create warning result
            warning, created = EarlyWarningResult.objects.get_or_create(
                student=enrollment.student,
                semester=enrollment.course_offering.semester,
                defaults={
                    'warning_level': 'yellow',
                    'attendance_risk_score': enrollment.attendance_percentage,
                    'calculated_at': timezone.now()
                }
            )
            
            if not created:
                # Update existing warning
                warning.attendance_risk_score = enrollment.attendance_percentage
                
                # Determine warning level based on attendance
                percentage = float(enrollment.attendance_percentage)
                if percentage < 50:
                    warning.warning_level = 'red'
                elif percentage < 65:
                    warning.warning_level = 'orange'
                else:
                    warning.warning_level = 'yellow'
                
                warning.calculated_at = timezone.now()
                warning.save()
    
    @staticmethod
    def check_and_update_all_enrollments(course_offering) -> Dict:
        """
        Check attendance for all enrollments in a course and update warnings.
        
        Args:
            course_offering: CourseOffering instance
            
        Returns:
            Summary of low attendance students
        """
        from apps.enrollments.models import Enrollment
        
        enrollments = Enrollment.objects.filter(
            course_offering=course_offering,
            enroll_status='enrolled'
        )
        
        low_attendance_count = 0
        warning_count = 0
        
        for enrollment in enrollments:
            # Recalculate percentage
            enrollment.update_attendance_percentage()
            
            if AttendanceThresholdService.is_low_attendance(enrollment):
                low_attendance_count += 1
                AttendanceWarningIntegrationService.update_low_attendance_warnings(enrollment)
                warning_count += 1
        
        return {
            'total_enrollments': enrollments.count(),
            'low_attendance_count': low_attendance_count,
            'warnings_issued': warning_count
        }


class StudentAttendanceViewService:
    """
    Service for generating student attendance views.
    """
    
    @staticmethod
    def get_student_course_attendance(student, semester=None) -> List[Dict]:
        """
        Get attendance summary for all courses a student is enrolled in.
        
        Args:
            student: Student instance
            semester: Optional semester filter
            
        Returns:
            List of attendance summaries per course
        """
        from apps.enrollments.models import Enrollment
        
        queryset = Enrollment.objects.filter(
            student=student,
            enroll_status='enrolled'
        ).select_related('course_offering', 'course_offering__course')
        
        if semester:
            queryset = queryset.filter(course_offering__semester=semester)
        
        results = []
        
        for enrollment in queryset:
            summary = AttendanceCalculationService.get_attendance_summary(enrollment)
            status = AttendanceThresholdService.get_attendance_status(enrollment)
            
            results.append({
                'enrollment_id': enrollment.pk,
                'course_code': enrollment.course_offering.course.code,
                'course_title': enrollment.course_offering.course.title,
                'semester': enrollment.course_offering.semester.name,
                'total_classes': summary['total_classes'],
                'attended_classes': summary['attended_classes'],
                'percentage': summary['percentage'],
                'status': status,
                'is_low_attendance': AttendanceThresholdService.is_low_attendance(enrollment),
                'status_breakdown': summary['status_breakdown']
            })
        
        return results
    
    @staticmethod
    def get_student_attendance_detail(enrollment) -> Dict:
        """
        Get detailed attendance records for a specific enrollment.
        
        Args:
            enrollment: Enrollment instance
            
        Returns:
            Detailed attendance information
        """
        from apps.attendance.models import AttendanceRecord
        
        records = AttendanceRecord.objects.filter(
            enrollment=enrollment
        ).order_by('-attendance_date')
        
        summary = AttendanceCalculationService.get_attendance_summary(enrollment)
        
        return {
            'course': {
                'code': enrollment.course_offering.course.code,
                'title': enrollment.course_offering.course.title,
            },
            'semester': enrollment.course_offering.semester.name,
            'summary': summary,
            'status': AttendanceThresholdService.get_attendance_status(enrollment),
            'records': [
                {
                    'date': record.attendance_date,
                    'status': record.status,
                    'status_display': record.get_status_display(),
                    'remarks': record.remarks,
                    'recorded_by': record.recorded_by.get_full_name() if record.recorded_by else None,
                }
                for record in records
            ]
        }
