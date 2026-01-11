from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from jobs.models import Job, JobApplication
from .serializers import JobSerializer, JobDetailSerializer, ApplicationSerializer, ApplicationCreateSerializer  # CHANGED

class JobListAPI(generics.ListAPIView):
    """Public API to list all active jobs (No auth required)"""
    queryset = Job.objects.filter(is_active=True)
    serializer_class = JobSerializer
    permission_classes = [permissions.AllowAny]

class JobDetailAPI(generics.RetrieveAPIView):
    """API to get job details (Requires authentication)"""
    queryset = Job.objects.filter(is_active=True)
    serializer_class = JobDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

class ApplyJobAPI(APIView):
    """API to apply for a job (Requires authentication)"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, job_id):
        try:
            job = Job.objects.get(id=job_id, is_active=True)
        except Job.DoesNotExist:
            return Response(
                {"error": "Job not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if already applied
        if JobApplication.objects.filter(job=job, applicant=request.user).exists():
            return Response(
                {"error": "You have already applied for this job"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Use ApplicationCreateSerializer instead of ApplicationSerializer
        serializer = ApplicationCreateSerializer(data=request.data)  # CHANGED
        if serializer.is_valid():
            application = serializer.save(
                job=job,
                applicant=request.user
            )
            return Response(
                {"message": "Application submitted successfully", "id": application.id},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MyApplicationsAPI(generics.ListAPIView):
    """API to view user's applications"""
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return JobApplication.objects.filter(applicant=self.request.user)