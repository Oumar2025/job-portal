from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    # JWT Authentication
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Job APIs
    path('jobs/', views.JobListAPI.as_view(), name='api_jobs'),
    path('jobs/<int:id>/', views.JobDetailAPI.as_view(), name='api_job_detail'),
    path('jobs/<int:job_id>/apply/', views.ApplyJobAPI.as_view(), name='api_apply_job'),
    path('my-applications/', views.MyApplicationsAPI.as_view(), name='api_my_applications'),
]