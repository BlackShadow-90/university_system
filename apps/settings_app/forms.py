from django import forms
from django.utils.translation import gettext_lazy as _
from .models import GradePolicy


class GradePolicyForm(forms.ModelForm):
    """Form for creating and updating grade policies"""
    
    class Meta:
        model = GradePolicy
        fields = [
            'name', 'max_gpa', 'passing_grade_point', 'gpa_warning_threshold',
            'cgpa_warning_threshold', 'attendance_warning_threshold',
            'gpa_drop_warning_threshold', 'description', 'is_default'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter policy name')
            }),
            'max_gpa': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'max': '10.00'
            }),
            'passing_grade_point': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'max': '10.00'
            }),
            'gpa_warning_threshold': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'max': '10.00'
            }),
            'cgpa_warning_threshold': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'max': '10.00'
            }),
            'attendance_warning_threshold': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'max': '100.00'
            }),
            'gpa_drop_warning_threshold': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'max': '10.00'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Optional description of this policy')
            }),
            'is_default': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def clean(self):
        cleaned_data = super().clean()
        max_gpa = cleaned_data.get('max_gpa')
        passing_grade_point = cleaned_data.get('passing_grade_point')
        gpa_warning_threshold = cleaned_data.get('gpa_warning_threshold')
        cgpa_warning_threshold = cleaned_data.get('cgpa_warning_threshold')
        attendance_warning_threshold = cleaned_data.get('attendance_warning_threshold')
        gpa_drop_warning_threshold = cleaned_data.get('gpa_drop_warning_threshold')
        
        # Validate logical relationships
        if max_gpa and passing_grade_point:
            if passing_grade_point > max_gpa:
                raise forms.ValidationError({
                    'passing_grade_point': _('Passing grade point cannot be greater than maximum GPA')
                })
        
        if max_gpa and gpa_warning_threshold:
            if gpa_warning_threshold > max_gpa:
                raise forms.ValidationError({
                    'gpa_warning_threshold': _('GPA warning threshold cannot be greater than maximum GPA')
                })
        
        if max_gpa and cgpa_warning_threshold:
            if cgpa_warning_threshold > max_gpa:
                raise forms.ValidationError({
                    'cgpa_warning_threshold': _('CGPA warning threshold cannot be greater than maximum GPA')
                })
        
        if attendance_warning_threshold:
            if not (0 <= attendance_warning_threshold <= 100):
                raise forms.ValidationError({
                    'attendance_warning_threshold': _('Attendance warning threshold must be between 0 and 100')
                })
        
        if gpa_drop_warning_threshold:
            if gpa_drop_warning_threshold < 0:
                raise forms.ValidationError({
                    'gpa_drop_warning_threshold': _('GPA drop warning threshold cannot be negative')
                })
        
        return cleaned_data
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name or len(name.strip()) < 3:
            raise forms.ValidationError(_('Policy name must be at least 3 characters long'))
        return name.strip()
    
    def clean_max_gpa(self):
        max_gpa = self.cleaned_data.get('max_gpa')
        if max_gpa and max_gpa <= 0:
            raise forms.ValidationError(_('Maximum GPA must be greater than 0'))
        return max_gpa
