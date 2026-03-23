from django.urls import path
from . import views

urlpatterns = [
    path('developer/', views.developer_dashboard, name='developer_dashboard'),
    path('developer/update/<int:task_id>/<str:status>/', views.update_task_status, name='update_task_status'),
    path('tester/', views.tester_dashboard, name='tester_dashboard'),
    path('tester/test/<int:task_id>/', views.test_task, name='test_task'),
]