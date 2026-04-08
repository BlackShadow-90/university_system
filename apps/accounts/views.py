import random
import string
from django.core.cache import cache
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView
from django.conf import settings

from .forms import (
    UserLoginForm, 
    AccountActivationForm,
    AdminActivationForm,
    PasswordResetRequestForm,
    PasswordResetVerifyForm,
    CustomPasswordChangeForm,
    ProfileUpdateForm
)
from .models import User
from apps.core.views import create_audit_log


class LoginView(View):
    """Custom login view with role-based redirect"""
    template_name = 'accounts/login.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return self._redirect_by_role(request.user)
        
        form = UserLoginForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = UserLoginForm(request, data=request.POST)
        
        if form.is_valid():
            user = form.get_user()
            
            # Only check if account is suspended
            if user.status == 'suspended':
                messages.error(request, _('Your account has been suspended. Please contact administration.'))
                return render(request, self.template_name, {'form': form})
            
            login(request, user)
            user.update_last_login()
            
            # Create audit log for login
            create_audit_log(
                request,
                action='login',
                module='Authentication',
                entity_type='User',
                entity_id=user.pk,
                entity_repr=user.get_full_name(),
                description=f'User {user.email} logged in'
            )
            
            messages.success(request, _('Welcome back, {}!').format(user.get_full_name()))
            
            # Redirect based on role
            return self._redirect_by_role(user)
        
        return render(request, self.template_name, {'form': form})
    
    def _redirect_by_role(self, user):
        """Redirect user based on their role"""
        if user.is_admin() or user.is_superuser:
            return redirect('admin_portal:admin_dashboard')
        elif user.is_teacher():
            return redirect('teacher_portal:teacher_dashboard')
        elif user.is_student():
            return redirect('student_portal:student_dashboard')
        return redirect('landing')


class LogoutView(View):
    """Logout view"""
    
    def get(self, request):
        logout(request)
        messages.success(request, _('You have been logged out successfully.'))
        return redirect('landing')


class AdminActivationView(View):
    """Admin view for activating student/teacher accounts by ID"""
    template_name = 'accounts/admin_activate.html'
    
    def get(self, request):
        # Only allow admin users
        if not request.user.is_authenticated or not (request.user.is_admin() or request.user.is_superuser):
            messages.error(request, _('You do not have permission to access this page.'))
            return redirect('accounts:login')
        
        form = AdminActivationForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        # Only allow admin users
        if not request.user.is_authenticated or not (request.user.is_admin() or request.user.is_superuser):
            messages.error(request, _('You do not have permission to access this page.'))
            return redirect('accounts:login')
        
        form = AdminActivationForm(request.POST)
        
        if form.is_valid():
            user = form.cleaned_data['user']
            profile = form.cleaned_data['profile']
            profile_type = form.cleaned_data['profile_type']
            password = form.cleaned_data['password']
            
            # Set password and activate
            user.set_password(password)
            user.status = 'active'
            user.save()
            
            # Show success message with credentials
            id_field = 'student_no' if profile_type == 'student' else 'teacher_no'
            user_id = getattr(profile, id_field)
            
            messages.success(
                request, 
                _('Account activated successfully! ID: %(id)s - Password: %(password)s. Give these credentials to the user.') % {
                    'id': user_id,
                    'password': password
                }
            )
            return redirect('accounts:admin_activate')
        
        return render(request, self.template_name, {'form': form})


class AccountActivationView(View):
    """View for activating student/teacher accounts - DISABLED"""
    
    def get(self, request):
        messages.info(request, _('Account activation is managed by administrators. Please contact your admin if you need assistance.'))
        return redirect('accounts:login')
    
    def post(self, request):
        messages.info(request, _('Account activation is managed by administrators. Please contact your admin if you need assistance.'))
        return redirect('accounts:login')


class PasswordResetRequestView(View):
    """View for requesting password reset with email and mobile verification"""
    template_name = 'accounts/password_reset_request.html'
    
    def get(self, request):
        form = PasswordResetRequestForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = PasswordResetRequestForm(request.POST)
        
        if form.is_valid():
            user = form.cleaned_data['user']
            email = form.cleaned_data['email']
            
            # Generate 6-digit verification code
            verification_code = ''.join(random.choices(string.digits, k=6))
            
            # Store in cache for 15 minutes
            cache_key = f'password_reset_{email}'
            cache.set(cache_key, {
                'code': verification_code,
                'user_id': user.id
            }, timeout=900)  # 15 minutes
            
            # TODO: Send SMS with verification code in production
            # For development, show the code in the message
            if settings.DEBUG:
                messages.success(
                    request,
                    _('Verification code sent to your mobile. (Dev code: %(code)s)') % {'code': verification_code}
                )
            else:
                messages.success(
                    request,
                    _('A verification code has been sent to your registered mobile number.')
                )
            
            # Redirect to verification page
            return redirect('accounts:password_reset_verify', email=email)
        
        return render(request, self.template_name, {'form': form})


class PasswordResetVerifyView(View):
    """View for verifying password reset code and setting new password"""
    template_name = 'accounts/password_reset_verify.html'
    
    def get(self, request, email):
        form = PasswordResetVerifyForm()
        return render(request, self.template_name, {'form': form, 'email': email})
    
    def post(self, request, email):
        form = PasswordResetVerifyForm(request.POST)
        
        if form.is_valid():
            code = form.cleaned_data['verification_code']
            new_password = form.cleaned_data['new_password']
            
            # Verify code from cache
            cache_key = f'password_reset_{email}'
            cached_data = cache.get(cache_key)
            
            if not cached_data:
                messages.error(request, _('Verification code has expired. Please request a new one.'))
                return redirect('accounts:password_reset_request')
            
            if cached_data['code'] != code:
                messages.error(request, _('Invalid verification code. Please try again.'))
                return render(request, self.template_name, {'form': form, 'email': email})
            
            # Reset password
            try:
                user = User.objects.get(id=cached_data['user_id'])
                user.set_password(new_password)
                user.save()
                
                # Clear cache
                cache.delete(cache_key)
                
                messages.success(request, _('Your password has been reset successfully. Please log in with your new password.'))
                return redirect('accounts:login')
            except User.DoesNotExist:
                messages.error(request, _('An error occurred. Please try again.'))
        
        return render(request, self.template_name, {'form': form, 'email': email})


@login_required
def profile_view(request):
    """User profile view"""
    user = request.user
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Your profile has been updated.'))
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=user)
    
    context = {
        'form': form,
        'user': user,
    }
    
    # Add role-specific profile info
    if user.is_student() and hasattr(user, 'student_profile'):
        context['student_profile'] = user.student_profile
    elif user.is_teacher() and hasattr(user, 'teacher_profile'):
        context['teacher_profile'] = user.teacher_profile
    
    return render(request, 'accounts/profile.html', context)


@login_required
def change_password_view(request):
    """Change password view"""
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('Your password has been changed successfully.'))
            return redirect('accounts:profile')
    else:
        form = CustomPasswordChangeForm(request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})
