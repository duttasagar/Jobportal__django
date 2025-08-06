from django.urls import path
from login import views
from rest_framework_simplejwt.views import TokenRefreshView
from .views import  LoginSerializerView, jobPostingView

urlpatterns = [
    path('registration/' ,views.RegisterUserView.as_view()),
    path('login/', views.LoginSerializerView.as_view()),
    path('hrdashboard/', views.jobPostingView.as_view()),
    path('apply/', views.ApplicationCreateView.as_view()),
    path('hrdashboard/<int:id>/', views.JobApplyView.as_view()),

    path('joblist/', views.CandidateApplicationList.as_view()),
    path('delete-job/<int:id>/', views.JobDelete.as_view()),
    path('hrdashboard/<int:id>/update/', views.JobUpdate.as_view()),
    path('delete/<int:id>/', views.JobApplicant.as_view()),
    path('send-otp/', views.SendOTPEmailView.as_view()),
    path('verify-otp/', views.VerifyOTPView.as_view()),
    path('search-jobs/', views.SearchPostedJob.as_view()),




]
