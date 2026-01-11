from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse
from django.db.utils import IntegrityError
from django.contrib.auth.models import User
from .models import Job, JobCategory, JobApplication

# ========== MODEL TESTS ==========
class TestJobCategoryModel(TestCase):
    """Test JobCategory model."""
    
    def setUp(self):
        self.category = JobCategory.objects.create(name='Technology')
    
    def test_category_creation(self):
        """Test category creation."""
        self.assertEqual(str(self.category), 'Technology')
        self.assertEqual(JobCategory.objects.count(), 1)
    
    def test_category_str_method(self):
        """Test string representation."""
        self.assertEqual(str(self.category), 'Technology')

class TestJobModel(TestCase):
    """Test Job model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='employer',
            email='employer@test.com',
            password='testpass123'
        )
        self.category = JobCategory.objects.create(name='IT')
        
        self.job = Job.objects.create(
            title='Python Developer',
            company='Tech Corp',
            location='Remote',
            description='Python developer needed',
            requirements='3+ years experience',
            salary='$80,000 - $100,000',
            job_type='full_time',
            category=self.category,
            posted_by=self.user,
            is_active=True
        )
    
    def test_job_creation(self):
        """Test job creation."""
        self.assertEqual(self.job.title, 'Python Developer')
        self.assertEqual(self.job.company, 'Tech Corp')
        self.assertTrue(self.job.is_active)
        self.assertEqual(Job.objects.count(), 1)
    
    def test_job_str_method(self):
        """Test string representation."""
        expected = 'Python Developer at Tech Corp'
        self.assertEqual(str(self.job), expected)
    
    def test_job_type_choices(self):
        """Test job type choices."""
        valid_choices = ['full_time', 'part_time', 'contract', 'remote']
        self.assertIn(self.job.job_type, valid_choices)
    
    def test_job_deactivation(self):
        """Test job deactivation."""
        self.job.is_active = False
        self.job.save()
        self.assertFalse(self.job.is_active)

class TestJobApplicationModel(TestCase):
    """Test JobApplication model."""
    
    def setUp(self):
        # Create user
        self.user = User.objects.create_user(
            username='applicant',
            email='applicant@test.com',
            password='testpass123'
        )
        
        # Create employer
        self.employer = User.objects.create_user(
            username='employer',
            email='employer@test.com',
            password='testpass123'
        )
        
        # Create category
        self.category = JobCategory.objects.create(name='IT')
        
        # Create job
        self.job = Job.objects.create(
            title='Python Developer',
            company='Tech Corp',
            location='Remote',
            description='Test job',
            requirements='Test requirements',
            salary='$80,000',
            job_type='full_time',
            category=self.category,
            posted_by=self.employer,
            is_active=True
        )
        
        # Create application
        self.application = JobApplication.objects.create(
            job=self.job,
            applicant=self.user,
            cover_letter='I am very interested in this position.',
            resume=SimpleUploadedFile('resume.pdf', b'fake pdf content'),
            status='pending'
        )
    
    def test_application_creation(self):
        """Test application creation."""
        self.assertEqual(self.application.job, self.job)
        self.assertEqual(self.application.applicant, self.user)
        self.assertEqual(self.application.status, 'pending')
        self.assertIsNotNone(self.application.applied_at)
    
    def test_application_str_method(self):
        """Test string representation."""
        expected = f'{self.user.username} - {self.job.title}'
        self.assertEqual(str(self.application), expected)
    
    def test_unique_together_constraint(self):
        """Test that user cannot apply twice for same job."""
        with self.assertRaises(IntegrityError):
            JobApplication.objects.create(
                job=self.job,
                applicant=self.user,
                cover_letter='Another application',
                resume=SimpleUploadedFile('resume2.pdf', b'content')
            )
    
    def test_application_status_choices(self):
        """Test status choices."""
        valid_statuses = ['pending', 'reviewed', 'accepted', 'rejected']
        self.assertIn(self.application.status, valid_statuses)

# ========== VIEW TESTS ==========
class TestJobViews(TestCase):
    """Test job views."""
    
    def setUp(self):
        self.client = Client()
        
        # Create users
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='adminpass123'
        )
        
        # Create category
        self.category = JobCategory.objects.create(name='IT')
        
        # Create job
        self.job = Job.objects.create(
            title='Test Job',
            company='Test Company',
            location='Test City',
            description='Test Description',
            requirements='Test Requirements',
            salary='$50,000',
            job_type='full_time',
            category=self.category,
            posted_by=self.admin_user,
            is_active=True
        )
    
    def test_home_view_public_access(self):
        """Test that home page is publicly accessible."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'jobs/home.html')
        self.assertContains(response, 'Find Your Dream Job')
    
    def test_job_detail_view_public_access(self):
        """Test that job detail page is publicly accessible."""
        response = self.client.get(reverse('job_detail', args=[self.job.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'jobs/job_detail.html')
        self.assertContains(response, self.job.title)
    
    def test_apply_job_view_requires_login(self):
        """Test that apply job requires login."""
        response = self.client.get(reverse('apply_job', args=[self.job.id]))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertRedirects(response, f'/accounts/login/?next=/job/{self.job.id}/apply/')
    
    def test_apply_job_view_authenticated(self):
        """Test apply job view for authenticated user."""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('apply_job', args=[self.job.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'jobs/apply_job.html')
    
    def test_apply_job_post(self):
        """Test submitting a job application."""
        self.client.login(username='testuser', password='testpass123')
        
        resume_file = SimpleUploadedFile(
            'resume.pdf',
            b'fake pdf content',
            content_type='application/pdf'
        )
        
        response = self.client.post(reverse('apply_job', args=[self.job.id]), {
            'cover_letter': 'I am very interested in this position.',
            'resume': resume_file
        })
        
        # Should redirect to job detail page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('job_detail', args=[self.job.id]))
        
        # Check that application was created
        self.assertTrue(JobApplication.objects.filter(
            job=self.job,
            applicant=self.user
        ).exists())
    
    def test_admin_dashboard_requires_admin(self):
        """Test that admin dashboard requires admin permissions."""
        # Regular user should be redirected
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302)  # Access denied
        
        # Admin user should have access
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'jobs/admin/admin_dashboard.html')  # CHANGED

    
    def test_create_job_view(self):
        """Test create job view for admin."""
        self.client.login(username='admin', password='adminpass123')
        
        response = self.client.get(reverse('create_job'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'jobs/admin/create_job.html')  # CHANGED
        
        # Test POST request
        response = self.client.post(reverse('create_job'), {
            'title': 'New Job Position',
            'company': 'New Company',
            'location': 'New City',
            'description': 'Job description here',
            'requirements': 'Requirements here',
            'salary': '$60,000',
            'job_type': 'remote',
            'category': self.category.id,
            'is_active': True
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(Job.objects.filter(title='New Job Position').exists())