from django.urls import path
from . import views

urlpatterns = [
    path('', views.notification_list, name='notification_list'),
    path('mark_read/<int:pk>/', views.mark_read, name='mark_read'),
]