from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User
from apps.departments.models import Department
from apps.programs.models import Program
from apps.semesters.models import Semester
from apps.teachers.models import Teacher


class Student(models.Model):
    """Student model - extends User"""
    
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('suspended', _('Suspended')),
        ('graduated', _('Graduated')),
        ('withdrawn', _('Withdrawn')),
        ('transferred', _('Transferred')),
        ('dropped_out', _('Dropped Out')),
    ]
    
    GENDER_CHOICES = [
        ('male', _('Male')),
        ('female', _('Female')),
        ('other', _('Other')),
        ('prefer_not_to_say', _('Prefer not to say')),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile',
        verbose_name=_('User Account')
    )
    
    student_no = models.CharField(
        _('Student ID'),
        max_length=20,
        unique=True
    )
    
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name='students',
        verbose_name=_('Department')
    )
    
    program = models.ForeignKey(
        Program,
        on_delete=models.PROTECT,
        related_name='students',
        verbose_name=_('Program/Major')
    )
    
    batch_year = models.CharField(
        _('Batch/Entry Year'),
        max_length=10
    )
    
    current_semester = models.ForeignKey(
        Semester,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_students',
        verbose_name=_('Current Semester')
    )
    
    advisor = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='advisees',
        verbose_name=_('Academic Advisor')
    )
    
    # Personal Information
    gender = models.CharField(
        _('Gender'),
        max_length=20,
        choices=GENDER_CHOICES,
        blank=True
    )
    
    date_of_birth = models.DateField(
        _('Date of Birth'),
        null=True,
        blank=True
    )
    
    nationality = models.CharField(
        _('Nationality'),
        max_length=50,
        blank=True
    )
    
    id_number = models.CharField(
        _('ID/Passport Number'),
        max_length=50,
        blank=True
    )
    
    # Guardian Information
    guardian_name = models.CharField(
        _('Guardian Name'),
        max_length=100,
        blank=True
    )
    
    guardian_phone = models.CharField(
        _('Guardian Phone'),
        max_length=20,
        blank=True
    )
    
    guardian_email = models.EmailField(
        _('Guardian Email'),
        blank=True
    )
    
    guardian_relationship = models.CharField(
        _('Relationship to Guardian'),
        max_length=50,
        blank=True
    )
    
    # Academic Information
    admission_date = models.DateField(
        _('Admission Date'),
        null=True,
        blank=True
    )
    
    expected_graduation = models.DateField(
        _('Expected Graduation Date'),
        null=True,
        blank=True
    )
    
    # Academic Status
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    
    # Academic Tracking
    total_credits_earned = models.DecimalField(
        _('Total Credits Earned'),
        max_digits=6,
        decimal_places=2,
        default=0
    )
    
    cgpa = models.DecimalField(
        _('CGPA'),
        max_digits=3,
        decimal_places=2,
        default=0.00
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'students'
        verbose_name = _('Student')
        verbose_name_plural = _('Students')
        ordering = ['student_no']

    def __str__(self):
        return f"{self.student_no} - {self.user.get_full_name()}"
    
    def get_full_name(self):
        """Return student's full name"""
        return self.user.get_full_name()
    
    @property
    def email(self):
        """Return student's email"""
        return self.user.email
    
    @property
    def phone(self):
        """Return student's phone"""
        return self.user.phone
    
    @property
    def is_active_student(self):
        """Check if student is currently active"""
        return self.status == 'active'
    
    def get_current_enrollments(self):
        """Get current semester enrollments"""
        if self.current_semester:
            return self.enrollments.filter(
                course_offering__semester=self.current_semester
            )
        return self.enrollments.none()
    
    def get_warning_level(self):
        """Get current warning level from latest warning result"""
        latest_warning = self.warning_results.order_by('-generated_at').first()
        if latest_warning:
            return latest_warning.warning_level
        return 'green'
