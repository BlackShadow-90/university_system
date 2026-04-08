from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.utils.translation import gettext_lazy as _

from .models import User


class UserLoginForm(AuthenticationForm):
    """Custom login form - accepts Email or Student/Teacher ID"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your Email or Student/Teacher ID'),
            'autofocus': True
        }),
        label=_('Email or ID')
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your password')
        }),
        label=_('Password')
    )


class AccountActivationForm(forms.Form):
    """Form for activating student/teacher accounts"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your email')
        }),
        label=_('Email')
    )
    activation_token = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter activation token')
        }),
        label=_('Activation Token')
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Create a password')
        }),
        label=_('Password'),
        min_length=8
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Confirm your password')
        }),
        label=_('Confirm Password')
    )
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError(_('Passwords do not match'))
        
        return cleaned_data
    
    def clean_activation_token(self):
        token = self.cleaned_data.get('activation_token')
        email = self.cleaned_data.get('email')
        
        if email and token:
            try:
                user = User.objects.get(email=email, activation_token=token)
                if not user.can_activate():
                    raise forms.ValidationError(_('This account cannot be activated or is already activated'))
            except User.DoesNotExist:
                raise forms.ValidationError(_('Invalid email or activation token'))
        
        return token


class AdminActivationForm(forms.Form):
    """Form for admin to activate student/teacher accounts by ID"""
    student_or_teacher_id = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter Student ID or Teacher ID')
        }),
        label=_('Student/Teacher ID')
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Set initial password')
        }),
        label=_('Initial Password'),
        min_length=6,
        help_text=_('Minimum 6 characters. User can change this after login.')
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Confirm password')
        }),
        label=_('Confirm Password'),
        min_length=6
    )
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError(_('Passwords do not match'))
        
        return cleaned_data
    
    def clean_student_or_teacher_id(self):
        student_or_teacher_id = self.cleaned_data.get('student_or_teacher_id', '').strip()
        
        if not student_or_teacher_id:
            raise forms.ValidationError(_('Please enter a Student ID or Teacher ID'))
        
        user = None
        profile = None
        
        # Try to find by Student ID
        from apps.students.models import Student
        from apps.teachers.models import Teacher
        
        try:
            student = Student.objects.get(student_no__iexact=student_or_teacher_id)
            user = student.user
            profile = student
            profile_type = 'student'
        except Student.DoesNotExist:
            # Try to find by Teacher ID
            try:
                teacher = Teacher.objects.get(teacher_no__iexact=student_or_teacher_id)
                user = teacher.user
                profile = teacher
                profile_type = 'teacher'
            except Teacher.DoesNotExist:
                raise forms.ValidationError(_('No student or teacher found with this ID'))
        
        # Check if user is already active
        if user.status == 'active':
            raise forms.ValidationError(_('This account is already activated'))
        
        # Store user and profile for view
        self.cleaned_data['user'] = user
        self.cleaned_data['profile'] = profile
        self.cleaned_data['profile_type'] = profile_type
        
        return student_or_teacher_id


class PasswordResetRequestForm(forms.Form):
    """Form for requesting password reset with email OR phone verification"""
    email_or_phone = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your email or mobile number')
        }),
        label=_('Email or Mobile Number')
    )
    
    def clean_email_or_phone(self):
        email_or_phone = self.cleaned_data.get('email_or_phone', '').strip()
        
        if not email_or_phone:
            raise forms.ValidationError(_('Please enter your email or mobile number'))
        
        user = None
        
        # Try to find by email first
        try:
            user = User.objects.get(email__iexact=email_or_phone)
        except User.DoesNotExist:
            # Try to find by phone
            try:
                user = User.objects.get(phone=email_or_phone)
            except User.DoesNotExist:
                raise forms.ValidationError(_('No user found with this email or mobile number'))
        
        # Store user for view to use
        self.cleaned_data['user'] = user
        self.cleaned_data['email'] = user.email
        
        return email_or_phone


class PasswordResetVerifyForm(forms.Form):
    """Form for verifying password reset with code"""
    verification_code = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter verification code'),
            'maxlength': '6'
        }),
        label=_('Verification Code'),
        max_length=6
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter new password')
        }),
        label=_('New Password'),
        min_length=8
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Confirm new password')
        }),
        label=_('Confirm Password'),
        min_length=8
    )
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError(_('Passwords do not match'))
        
        return cleaned_data


class CustomPasswordChangeForm(PasswordChangeForm):
    """Custom password change form with Bootstrap styling"""
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Current password')
        }),
        label=_('Current Password')
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('New password')
        }),
        label=_('New Password')
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Confirm new password')
        }),
        label=_('Confirm New Password')
    )


class ProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile"""
    class Meta:
        model = User
        fields = ['full_name_en', 'full_name_zh', 'phone', 'avatar']
        widgets = {
            'full_name_en': forms.TextInput(attrs={'class': 'form-control'}),
            'full_name_zh': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }
