from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('analyst/', views.analyst_dashboard, name='analyst_dashboard'),
    path('analyst/create/', views.create_project, name='create_project'),
    path('curator/', views.curator_dashboard, name='curator_dashboard'),
    path('curator/assign_task/<int:task_id>/', views.assign_task, name='assign_task'),
]