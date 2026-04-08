from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator

from apps.courses.models import Course
from apps.semesters.models import Semester
from apps.teachers.models import Teacher


class CourseOffering(models.Model):
    """Course offering for a specific semester"""
    
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('open', _('Open for Registration')),
        ('in_progress', _('In Progress')),
        ('grading', _('Grading')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]
    
    DAY_CHOICES = [
        ('mon', _('Monday')),
        ('tue', _('Tuesday')),
        ('wed', _('Wednesday')),
        ('thu', _('Thursday')),
        ('fri', _('Friday')),
        ('sat', _('Saturday')),
        ('sun', _('Sunday')),
    ]
    
    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name='offerings',
        verbose_name=_('Course')
    )
    
    semester = models.ForeignKey(
        Semester,
        on_delete=models.PROTECT,
        related_name='course_offerings',
        verbose_name=_('Semester')
    )
    
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.PROTECT,
        related_name='course_offerings',
        verbose_name=_('Instructor')
    )
    
    section_name = models.CharField(
        _('Section'),
        max_length=20,
        default='01',
        help_text=_('e.g., 01, 02, A, B')
    )
    
    room = models.CharField(
        _('Classroom'),
        max_length=50,
        blank=True
    )
    
    day_of_week = models.CharField(
        _('Day of Week'),
        max_length=10,
        choices=DAY_CHOICES,
        blank=True
    )
    
    start_time = models.TimeField(
        _('Start Time'),
        null=True,
        blank=True
    )
    
    end_time = models.TimeField(
        _('End Time'),
        null=True,
        blank=True
    )
    
    capacity = models.PositiveIntegerField(
        _('Capacity'),
        default=50,
        validators=[MinValueValidator(1)]
    )
    
    enrolled_count = models.PositiveIntegerField(
        _('Enrolled Count'),
        default=0
    )
    
    waiting_count = models.PositiveIntegerField(
        _('Waiting List Count'),
        default=0
    )
    
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    
    is_grade_published = models.BooleanField(
        _('Grades Published'),
        default=False
    )
    
    grade_published_at = models.DateTimeField(
        _('Grades Published At'),
        null=True,
        blank=True
    )
    
    syllabus = models.FileField(
        _('Syllabus'),
        upload_to='syllabi/%Y/%m/',
        blank=True,
        null=True
    )
    
    notes = models.TextField(_('Notes'), blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'course_offerings'
        verbose_name = _('Course Offering')
        verbose_name_plural = _('Course Offerings')
        unique_together = ['course', 'semester', 'section_name']
        ordering = ['semester', 'course__code', 'section_name']

    def __str__(self):
        return f"{self.course.code}-{self.section_name} ({self.semester})"
    
    @property
    def available_seats(self):
        """Return available seats"""
        return max(0, self.capacity - self.enrolled_count)
    
    @property
    def is_full(self):
        """Check if course is full"""
        return self.enrolled_count >= self.capacity
    
    @property
    def schedule_display(self):
        """Return formatted schedule string"""
        if self.day_of_week and self.start_time and self.end_time:
            return f"{self.get_day_of_week_display()} {self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')}"
        return _('Not scheduled')
    
    def update_enrollment_count(self):
        """Update enrolled and waiting counts"""
        self.enrolled_count = self.enrollments.filter(
            enroll_status='enrolled'
        ).count()
        self.waiting_count = self.enrollments.filter(
            enroll_status='waiting'
        ).count()
        self.save(update_fields=['enrolled_count', 'waiting_count'])
