from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Task, TaskStatus

@login_required
def developer_dashboard(request):
    tasks = Task.objects.filter(assigned_to=request.user).exclude(status=TaskStatus.DONE).order_by('deadline')
    return render(request, 'tasks/developer_dashboard.html', {'tasks': tasks})