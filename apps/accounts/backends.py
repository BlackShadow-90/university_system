"""
Custom authentication backends for the university system.
Allows login with Email, Student ID, or Teacher ID.
"""
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from apps.accounts.models import User
from apps.students.models import Student
from apps.teachers.models import Teacher


class EmailOrIDBackend(ModelBackend):
    """
    Custom authentication backend that allows users to log in with:
    - Email address
    - Student ID (student_no)
    - Teacher ID (teacher_no)
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None
        
        user = None
        
        # Try to find user by email first
        try:
            user = User.objects.get(email__iexact=username)
        except User.DoesNotExist:
            # Try to find by Student ID
            try:
                student = Student.objects.get(student_no__iexact=username)
                user = student.user
            except Student.DoesNotExist:
                # Try to find by Teacher ID
                try:
                    teacher = Teacher.objects.get(teacher_no__iexact=username)
                    user = teacher.user
                except Teacher.DoesNotExist:
                    return None
        
        # Check password and return user if valid
        if user and user.check_password(password):
            return user
        
        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
