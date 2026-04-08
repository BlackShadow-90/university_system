"""
Core application services and utilities
"""
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import PermissionDenied
from functools import wraps
from decimal import Decimal

from apps.enrollments.models import Enrollment

# Import unified calculation services
from apps.core.academic_services import (
    FinalScoreCalculationService,
    GPACalculationService,
    AcademicRecalculationService,
)


def role_required(allowed_roles):
    """
    Decorator to check if user has required role
    Usage: @role_required(['admin', 'teacher'])
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied(_('Authentication required'))
            
            user_role = request.user.role.code if request.user.role else None
            
            if user_role not in allowed_roles and not request.user.is_superuser:
                raise PermissionDenied(_('You do not have permission to access this page'))
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def admin_required(view_func):
    """Decorator for admin-only views"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied(_('Authentication required'))
        
        if not (request.user.is_admin() or request.user.is_superuser):
            raise PermissionDenied(_('Admin access required'))
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def teacher_required(view_func):
    """Decorator for teacher-only views"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied(_('Authentication required'))
        
        if not (request.user.is_teacher() or request.user.is_admin() or request.user.is_superuser):
            raise PermissionDenied(_('Teacher access required'))
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def student_required(view_func):
    """Decorator for student-only views"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied(_('Authentication required'))
        
        if not (request.user.is_student() or request.user.is_admin() or request.user.is_superuser):
            raise PermissionDenied(_('Student access required'))
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


class WarningEngine:
    """Service class for early warning calculations"""
    
    RISK_WEIGHTS = {
        'attendance': 0.25,
        'course_failures': 0.25,
        'gpa': 0.20,
        'gpa_trend': 0.10,
        'missing_assessment': 0.10,
        'teacher_flag': 0.10,
    }
    
    @classmethod
    def calculate_risk_score(cls, risk_factors):
        """
        Calculate overall risk score from individual risk factors
        risk_factors: dict with keys matching RISK_WEIGHTS and values 0-100
        """
        total_score = 0
        total_weight = 0
        
        for category, weight in cls.RISK_WEIGHTS.items():
            if category in risk_factors:
                total_score += risk_factors[category] * weight
                total_weight += weight
        
        if total_weight == 0:
            return 0
        
        # Normalize to 0-100 scale
        return round(total_score / total_weight, 2)
    
    @classmethod
    def get_warning_level(cls, risk_score):
        """Determine warning level from risk score"""
        if risk_score >= 75:
            return 'red'  # Critical
        elif risk_score >= 50:
            return 'orange'  # Serious
        elif risk_score >= 25:
            return 'yellow'  # Mild
        else:
            return 'green'  # Stable
    
    @staticmethod
    def get_interventions(risk_factors):
        """Get recommended interventions based on risk factors"""
        interventions = []
        
        if 'attendance' in risk_factors and risk_factors['attendance'] > 50:
            interventions.append(_('Increase attendance immediately'))
            interventions.append(_('Meet with course instructor'))
        
        if 'gpa' in risk_factors and risk_factors['gpa'] > 50:
            interventions.append(_('Attend tutoring sessions'))
            interventions.append(_('Meet with academic advisor'))
        
        if 'course_failures' in risk_factors and risk_factors['course_failures'] > 50:
            interventions.append(_('Retake failed courses'))
            interventions.append(_('Develop study plan with advisor'))
        
        if 'missing_assessment' in risk_factors and risk_factors['missing_assessment'] > 0:
            interventions.append(_('Complete missing assessments immediately'))
            interventions.append(_('Contact course instructor'))
        
        if 'gpa_trend' in risk_factors and risk_factors['gpa_trend'] > 50:
            interventions.append(_('Analyze factors affecting performance decline'))
            interventions.append(_('Seek counseling if needed'))
        
        return interventions
