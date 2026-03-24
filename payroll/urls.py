from django.urls import path
from . import views

urlpatterns = [
    path('', views.accountant_dashboard, name='accountant_dashboard'),
]