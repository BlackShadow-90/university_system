import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class Role(models.Model):
    """Role model for user roles (Admin, Teacher, Student)"""
    name = models.CharField(_('Role Name'), max_length=50, unique=True)
    code = models.CharField(_('Role Code'), max_length=20, unique=True)
    description = models.TextField(_('Description'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'roles'
        verbose_name = _('Role')
        verbose_name_plural = _('Roles')

    def __str__(self):
        return self.name


class Permission(models.Model):
    """Permission model for granular permissions"""
    name = models.CharField(_('Permission Name'), max_length=100)
    code = models.CharField(_('Permission Code'), max_length=50, unique=True)
    description = models.TextField(_('Description'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'permissions'
        verbose_name = _('Permission')
        verbose_name_plural = _('Permissions')

    def __str__(self):
        return self.name


class RolePermission(models.Model):
    """Many-to-many relationship between Role and Permission"""
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_permissions')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name='permission_roles')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'role_permissions'
        unique_together = ['role', 'permission']
        verbose_name = _('Role Permission')
        verbose_name_plural = _('Role Permissions')


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User model with bilingual support"""
    
    STATUS_CHOICES = [
        ('pending', _('Pending Activation')),
        ('active', _('Active')),
        ('suspended', _('Suspended')),
        ('inactive', _('Inactive')),
    ]
    
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    full_name_en = models.CharField(_('Full Name (English)'), max_length=100)
    full_name_zh = models.CharField(_('Full Name (Chinese)'), max_length=100, blank=True)
    email = models.EmailField(_('Email'), unique=True)
    phone = models.CharField(_('Phone'), max_length=20, blank=True)
    
    role = models.ForeignKey(
        Role, 
        on_delete=models.PROTECT, 
        related_name='users',
        verbose_name=_('Role')
    )
    
    avatar = models.ImageField(
        _('Avatar'), 
        upload_to='avatars/%Y/%m/', 
        blank=True, 
        null=True
    )
    
    status = models.CharField(
        _('Status'), 
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    
    is_staff = models.BooleanField(_('Staff Status'), default=False)
    is_superuser = models.BooleanField(_('Superuser Status'), default=False)
    is_active = models.BooleanField(_('Active'), default=True)
    
    last_login_at = models.DateTimeField(_('Last Login'), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name_en']
    
    objects = UserManager()
    
    class Meta:
        db_table = 'users'
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.full_name_en} ({self.email})"
    
    def get_full_name(self):
        """Return full name based on preference"""
        return self.full_name_en or self.full_name_zh
    
    def get_short_name(self):
        """Return short name"""
        return self.full_name_en.split()[0] if self.full_name_en else self.email
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login_at = timezone.now()
        self.save(update_fields=['last_login_at'])
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role.code == 'admin' if self.role else False
    
    def is_teacher(self):
        """Check if user is teacher"""
        return self.role.code == 'teacher' if self.role else False
    
    def is_student(self):
        """Check if user is student"""
        return self.role.code == 'student' if self.role else False
    
    def can_activate(self):
        """Check if account can be activated"""
        return self.status == 'pending'
    
    def activate(self):
        """Activate the account"""
        self.status = 'active'
        self.save(update_fields=['status'])
