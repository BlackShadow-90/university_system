"""
Tests for accounts app
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.accounts.models import Role, Permission, RolePermission

User = get_user_model()


class RoleModelTests(TestCase):
    """Test Role model"""
    
    def setUp(self):
        self.role = Role.objects.create(
            name='Test Role',
            code='test_role',
            description='Test role description'
        )
    
    def test_role_creation(self):
        """Test role can be created"""
        self.assertEqual(self.role.name, 'Test Role')
        self.assertEqual(self.role.code, 'test_role')
        self.assertEqual(str(self.role), 'Test Role')


class UserModelTests(TestCase):
    """Test User model"""
    
    def setUp(self):
        self.admin_role = Role.objects.create(name='Administrator', code='admin')
        self.user = User.objects.create_user(
            email='test@example.com',
            full_name_en='Test User',
            password='testpass123',
            role=self.admin_role
        )
    
    def test_user_creation(self):
        """Test user can be created"""
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.get_full_name(), 'Test User')
        self.assertTrue(self.user.check_password('testpass123'))
        self.assertEqual(str(self.user), 'Test User (test@example.com)')
    
    def test_user_is_admin(self):
        """Test admin role check"""
        self.assertTrue(self.user.is_admin())
    
    def test_update_last_login(self):
        """Test last login timestamp update"""
        self.assertIsNone(self.user.last_login_at)
        self.user.update_last_login()
        self.assertIsNotNone(self.user.last_login_at)


class AuthenticationViewTests(TestCase):
    """Test authentication views"""
    
    def setUp(self):
        self.client = Client()
        self.admin_role = Role.objects.create(name='Administrator', code='admin')
        self.user = User.objects.create_user(
            email='test@example.com',
            full_name_en='Test User',
            password='testpass123',
            role=self.admin_role,
            status='active'
        )
    
    def test_login_view_get(self):
        """Test login page loads"""
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
    
    def test_login_view_post_valid(self):
        """Test valid login"""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'test@example.com',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after login
    
    def test_login_view_post_invalid(self):
        """Test invalid login"""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'test@example.com',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)  # Stay on page
