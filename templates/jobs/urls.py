from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('job/<int:job_id>/', views.job_detail_view, name='job_detail'),
    path('job/<int:job_id>/apply/', views.apply_job_view, name='apply_job'),
    
    # Admin routes
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('create-job/', views.create_job, name='create_job'),
    path('job/<int:job_id>/applications/', views.view_applications, name='view_applications'),
]