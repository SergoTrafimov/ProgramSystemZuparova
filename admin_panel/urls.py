from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('users/', views.user_list, name='admin_user_list'),
    path('users/<int:user_id>/edit/', views.user_edit, name='admin_user_edit'),
    path('projects/', views.project_list, name='admin_project_list'),
    path('projects/<str:project_id>/edit/', views.project_edit, name='admin_project_edit'),
    path('projects/<str:project_id>/delete/', views.project_delete, name='admin_project_delete'),
    path('tasks/', views.task_list, name='admin_task_list'),
    path('tasks/<int:task_id>/edit/', views.task_edit, name='admin_task_edit'),
]