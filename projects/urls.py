from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('analyst/', views.analyst_dashboard, name='analyst_dashboard'),
    path('analyst/create/', views.create_project, name='create_project'),
    path('analyst/messages/', views.analyst_messages, name='analyst_messages'),
    path('analyst/messages/<int:message_id>/', views.view_message, name='view_message'),
    path('analyst/messages/<int:message_id>/close/', views.close_message, name='close_message'),
    path('analyst/messages/<int:message_id>/create_project/', views.create_project_from_message, name='create_project_from_message'),
    path('curator/', views.curator_dashboard, name='curator_dashboard'),
    path('curator/assign_task/<int:task_id>/', views.assign_task, name='assign_task'),
    path('project/<str:project_id>/tasks/', views.project_tasks, name='project_tasks'),
    path('project/<str:project_id>/dialog/', views.project_dialog, name='project_dialog'),
]