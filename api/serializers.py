from rest_framework import serializers
from jobs.models import Job, JobApplication

class JobSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Job
        fields = ['id', 'title', 'company', 'location', 'salary', 
                 'job_type', 'category_name', 'created_at']

class JobDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    posted_by_name = serializers.CharField(source='posted_by.username', read_only=True)
    
    class Meta:
        model = Job
        fields = ['id', 'title', 'company', 'location', 'description',
                 'requirements', 'salary', 'job_type', 'category_name',
                 'posted_by_name', 'created_at']

class ApplicationSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job.title', read_only=True)
    company_name = serializers.CharField(source='job.company', read_only=True)
    
    class Meta:
        model = JobApplication
        fields = ['id', 'job', 'job_title', 'company_name', 'cover_letter',
                 'resume', 'applied_at', 'status']
        read_only_fields = ['applied_at', 'status']

# ADD THIS NEW SERIALIZER
class ApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = ['cover_letter', 'resume']
        extra_kwargs = {
            'cover_letter': {'required': True},
            'resume': {'required': True}
        }        