from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),  # для логина/логаута
    path('projects/', include('projects.urls')),
    path('tasks/', include('tasks.urls')),
    path('payroll/', include('payroll.urls')),

]