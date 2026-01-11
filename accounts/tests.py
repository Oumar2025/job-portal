from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class TestAuthentication(TestCase):
    """Test authentication views."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
    
    def test_register_view_get(self):
        """Test register page GET request."""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')
    
    def test_register_view_post(self):
        """Test user registration."""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!'
        })
        
        # Should redirect to home after successful registration
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
        
        # Check that user was created
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertTrue(User.objects.filter(email='newuser@test.com').exists())
    
    def test_login_view_get(self):
        """Test login page GET request."""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
    
    def test_login_view_post(self):
        """Test user login."""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Should redirect to home after successful login
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        
        self.assertEqual(response.status_code, 200)  # Stays on login page
        self.assertTemplateUsed(response, 'accounts/login.html')
    
    def test_logout_view(self):
        """Test user logout."""
        # Login first
        self.client.login(username='testuser', password='testpass123')
        
        # Check that user is logged in
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'Welcome, testuser')
        
        # Logout
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
        
        # Check that user is logged out
        response = self.client.get(reverse('home'))
        self.assertNotContains(response, 'Welcome, testuser')

class TestUserProfile(TestCase):
    """Test user profile views."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='profileuser',
            email='profile@test.com',
            password='testpass123'
        )
    
    def test_profile_view_requires_login(self):
        """Test that profile requires login."""
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_profile_view_authenticated(self):
        """Test profile view for authenticated user."""
        self.client.login(username='profileuser', password='testpass123')
        response = self.client.get(reverse('profile'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')