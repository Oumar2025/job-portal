import json
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from django.urls import reverse
from jobs.models import Job, JobCategory, JobApplication
from django.core.files.uploadedfile import SimpleUploadedFile

class TestJobAPI(APITestCase):
    """Test Job API endpoints."""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create users
        self.user = User.objects.create_user(
            username='apiuser',
            email='api@test.com',
            password='testpass123'
        )
        
        self.admin_user = User.objects.create_user(
            username='apiadmin',
            email='adminapi@test.com',
            password='adminpass123'
        )
        
        # Create category
        self.category = JobCategory.objects.create(name='API Category')
        
        # Create jobs
        self.job1 = Job.objects.create(
            title='API Job 1',
            company='API Company',
            location='API City',
            description='API Description',
            requirements='API Requirements',
            salary='$70,000',
            job_type='full_time',
            category=self.category,
            posted_by=self.admin_user,
            is_active=True
        )
        
        self.job2 = Job.objects.create(
            title='API Job 2',
            company='API Company 2',
            location='API City 2',
            description='API Description 2',
            requirements='API Requirements 2',
            salary='$80,000',
            job_type='remote',
            category=self.category,
            posted_by=self.admin_user,
            is_active=False  # Inactive job
        )
    
    def test_get_jobs_public_access(self):
        """Test that jobs API is publicly accessible."""
        response = self.client.get(reverse('api_jobs'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only active jobs
    
    def test_get_job_detail_requires_auth(self):
        """Test that job detail requires authentication."""
        response = self.client.get(reverse('api_job_detail', args=[self.job1.id]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_job_detail_with_auth(self):
        """Test job detail with authentication."""
        # Get JWT token
        token_response = self.client.post(reverse('token_obtain_pair'), {
            'username': 'apiuser',
            'password': 'testpass123'
        })
        token = token_response.data['access']
        
        # Use token to access protected endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(reverse('api_job_detail', args=[self.job1.id]))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.job1.title)
        self.assertEqual(response.data['company'], self.job1.company)
    
    def test_apply_job_api(self):
        """Test applying for a job through API."""
        # Get JWT token
        token_response = self.client.post(reverse('token_obtain_pair'), {
            'username': 'apiuser',
            'password': 'testpass123'
        })
        token = token_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Create a resume file
        resume_file = SimpleUploadedFile(
            'api_resume.pdf',
            b'fake pdf content for api',
            content_type='application/pdf'
        )
        
        # Apply for job
        response = self.client.post(
            reverse('api_apply_job', args=[self.job1.id]),
            {
                'cover_letter': 'I want to apply via API',
                'resume': resume_file
            },
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Application submitted successfully')
        
        # Check that application was created
        self.assertTrue(JobApplication.objects.filter(
            job=self.job1,
            applicant=self.user
        ).exists())
    
    def test_apply_job_twice_api(self):
        """Test that user cannot apply twice for same job via API."""
        # First application
        token_response = self.client.post(reverse('token_obtain_pair'), {
            'username': 'apiuser',
            'password': 'testpass123'
        })
        token = token_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        resume_file = SimpleUploadedFile('resume.pdf', b'content')
        
        # First application should succeed
        response1 = self.client.post(
            reverse('api_apply_job', args=[self.job1.id]),
            {
                'cover_letter': 'First application',
                'resume': resume_file
            },
            format='multipart'
        )
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Second application should fail
        resume_file2 = SimpleUploadedFile('resume2.pdf', b'content2')
        response2 = self.client.post(
            reverse('api_apply_job', args=[self.job1.id]),
            {
                'cover_letter': 'Second application',
                'resume': resume_file2
            },
            format='multipart'
        )
        
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response2.data['error'], 'You have already applied for this job')
    
    def test_my_applications_api(self):
        """Test retrieving user's applications via API."""
        # Create an application first
        JobApplication.objects.create(
            job=self.job1,
            applicant=self.user,
            cover_letter='Test application',
            resume='resume.pdf'
        )
        
        # Get token
        token_response = self.client.post(reverse('token_obtain_pair'), {
            'username': 'apiuser',
            'password': 'testpass123'
        })
        token = token_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Get my applications
        response = self.client.get(reverse('api_my_applications'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['job_title'], self.job1.title)