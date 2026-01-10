from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Job, JobApplication, JobCategory
from .forms import JobForm, ApplicationForm

def home_view(request):
    jobs = Job.objects.filter(is_active=True).order_by('-created_at')
    categories = JobCategory.objects.all()
    return render(request, 'jobs/home.html', {
        'jobs': jobs,
        'categories': categories
    })

def job_detail_view(request, job_id):
    job = get_object_or_404(Job, id=job_id, is_active=True)
    has_applied = False
    if request.user.is_authenticated:
        has_applied = JobApplication.objects.filter(
            job=job, 
            applicant=request.user
        ).exists()
    
    return render(request, 'jobs/job_detail.html', {
        'job': job,
        'has_applied': has_applied
    })

@login_required
def apply_job_view(request, job_id):
    job = get_object_or_404(Job, id=job_id, is_active=True)
    
    # Check if already applied
    if JobApplication.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, 'You have already applied for this job.')
        return redirect('job_detail', job_id=job_id)
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            messages.success(request, 'Application submitted successfully!')
            return redirect('job_detail', job_id=job_id)
    else:
        form = ApplicationForm()
    
    return render(request, 'jobs/apply_job.html', {
        'form': form,
        'job': job
    })

# Admin views
def is_admin(user):
    return user.is_superuser or user.is_staff

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    jobs = Job.objects.filter(posted_by=request.user)
    total_applications = JobApplication.objects.filter(job__posted_by=request.user).count()
    
    return render(request, 'jobs/admin_dashboard.html', {
        'jobs': jobs,
        'total_applications': total_applications
    })

@login_required
@user_passes_test(is_admin)
def create_job(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            messages.success(request, 'Job created successfully!')
            return redirect('admin_dashboard')
    else:
        form = JobForm()
    
    return render(request, 'jobs/create_job.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def view_applications(request, job_id):
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)
    applications = job.applications.all()
    
    return render(request, 'jobs/view_applications.html', {
        'job': job,
        'applications': applications
    })