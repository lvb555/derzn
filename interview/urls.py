from django.urls import path

from . import views

# app_name = 'interview'

urlpatterns = [
    path('interview_index/', views.interview_index, name='interview_index'),
    path('interview_detail/<int:interview_id>/', views.interview_detail, name='interview_detail'),
    path('interview_create/', views.interview_create, name='interview_create'),
    path('interview_edit/<int:interview_id>/', views.interview_edit, name='interview_edit'),
]
