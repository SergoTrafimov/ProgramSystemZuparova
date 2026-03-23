from django.urls import path
from . import views

urlpatterns = [
    path('project/<str:project_id>/feedback/', views.project_feedback, name='project_feedback'),
]