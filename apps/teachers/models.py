from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User
from apps.departments.models import Department


class Teacher(models.Model):
    """Teacher/Professor model - extends User"""
    
    TITLE_CHOICES = [
        ('lecturer', _('Lecturer')),
        ('assistant_professor', _('Assistant Professor')),
        ('associate_professor', _('Associate Professor')),
        ('professor', _('Professor')),
        ('senior_professor', _('Senior Professor')),
        ('instructor', _('Instructor')),
        ('adjunct', _('Adjunct Professor')),
        ('visiting', _('Visiting Professor')),
    ]
    
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('on_leave', _('On Leave')),
        ('retired', _('Retired')),
        ('resigned', _('Resigned')),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='teacher_profile',
        verbose_name=_('User Account')
    )
    
    teacher_no = models.CharField(
        _('Teacher ID'),
        max_length=20,
        unique=True
    )
    
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name='teachers',
        verbose_name=_('Department')
    )
    
    title = models.CharField(
        _('Title'),
        max_length=30,
        choices=TITLE_CHOICES,
        default='lecturer'
    )
    
    specialization = models.CharField(
        _('Specialization/Research Area'),
        max_length=200,
        blank=True
    )
    
    office_location = models.CharField(
        _('Office Location'),
        max_length=100,
        blank=True
    )
    
    office_hours = models.TextField(
        _('Office Hours'),
        blank=True,
        help_text=_('e.g., Mon 10:00-12:00, Wed 14:00-16:00')
    )
    
    bio = models.TextField(_('Biography'), blank=True)
    
    # Profile fields for research and academic info
    research_interests = models.TextField(
        _('Research Interests'),
        blank=True,
        help_text=_('Describe your research interests and areas of expertise')
    )
    
    research_abilities = models.TextField(
        _('Research Abilities'),
        blank=True,
        help_text=_('List your research skills, methodologies, and technical abilities')
    )
    
    publications = models.TextField(
        _('Publications'),
        blank=True,
        help_text=_('List your key publications, papers, and research works')
    )
    
    education_background = models.TextField(
        _('Education Background'),
        blank=True,
        help_text=_('Your academic degrees and educational history')
    )
    
    teaching_interests = models.TextField(
        _('Teaching Interests'),
        blank=True,
        help_text=_('Courses and subjects you are interested in teaching')
    )
    
    professional_experience = models.TextField(
        _('Professional Experience'),
        blank=True,
        help_text=_('Your work experience and professional background')
    )
    
    awards_and_honors = models.TextField(
        _('Awards and Honors'),
        blank=True,
        help_text=_('Awards, recognitions, and honors received')
    )
    
    website = models.URLField(
        _('Personal Website'),
        blank=True,
        max_length=200
    )
    
    linkedin = models.URLField(
        _('LinkedIn Profile'),
        blank=True,
        max_length=200
    )
    
    join_date = models.DateField(_('Join Date'))
    
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'teachers'
        verbose_name = _('Teacher')
        verbose_name_plural = _('Teachers')
        ordering = ['teacher_no']

    def __str__(self):
        return f"{self.teacher_no} - {self.user.get_full_name()}"
    
    def get_full_name(self):
        """Return teacher's full name"""
        return self.user.get_full_name()
    
    @property
    def email(self):
        """Return teacher's email"""
        return self.user.email
    
    @property
    def phone(self):
        """Return teacher's phone"""
        return self.user.phone
    
    @property
    def is_active_teacher(self):
        """Check if teacher is currently active"""
        return self.status == 'active'
