from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Custom user manager for the User model"""
    
    def create_user(self, email, full_name_en, password=None, **extra_fields):
        """Create and save a regular user"""
        if not email:
            raise ValueError(_('Email is required'))
        if not full_name_en:
            raise ValueError(_('Full name is required'))
        
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            full_name_en=full_name_en,
            **extra_fields
        )
        
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, full_name_en, password=None, **extra_fields):
        """Create and save a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('status', 'active')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True'))
        
        # Get or create admin role
        from apps.accounts.models import Role
        admin_role, _ = Role.objects.get_or_create(
            code='admin',
            defaults={'name': 'Administrator', 'description': 'System Administrator'}
        )
        extra_fields.setdefault('role', admin_role)
        
        return self.create_user(email, full_name_en, password, **extra_fields)
