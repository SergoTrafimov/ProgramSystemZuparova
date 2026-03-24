from django.urls import path
from . import views

urlpatterns = [
    path('project/<str:project_id>/feedback/', views.project_feedback, name='project_feedback'),
    path('dashboard/', views.client_dashboard, name='client_dashboard'),
    path('create/', views.create_client_message, name='create_client_message'),
    path('message/<int:message_id>/', views.view_client_message, name='view_client_message'),
]