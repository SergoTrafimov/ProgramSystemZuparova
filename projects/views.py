from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Project
from .forms import ProjectForm
from tasks.models import Task
from tasks.forms import TaskForm

def is_analyst(user):
    return user.is_authenticated and user.profile.role == 'analyst'

def is_curator(user):
    return user.is_authenticated and user.profile.role == 'curator'

def index(request):
    # Перенаправление по ролям
    if request.user.is_authenticated:
        role = request.user.profile.role
        if role == 'analyst':
            return redirect('analyst_dashboard')
        elif role == 'curator':
            return redirect('curator_dashboard')
        elif role == 'dev':
            return redirect('developer_dashboard')
        elif role == 'tester':
            return redirect('tester_dashboard')
        elif role == 'accountant':
            return redirect('accountant_dashboard')
    return render(request, 'projects/index.html')

@login_required
@user_passes_test(is_analyst)
def analyst_dashboard(request):
    projects = Project.objects.filter(created_by=request.user)
    return render(request, 'projects/analyst/dashboard.html', {'projects': projects})

@login_required
@user_passes_test(is_analyst)
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()  # сигнал назначит куратора
            messages.success(request, 'Проект создан и куратор назначен.')
            return redirect('analyst_dashboard')
    else:
        form = ProjectForm()
    return render(request, 'projects/analyst/create_project.html', {'form': form})

@login_required
@user_passes_test(is_curator)
def curator_dashboard(request):
    projects = Project.objects.filter(curator=request.user)
    tasks = Task.objects.filter(project__curator=request.user).exclude(status='completed')
    return render(request, 'projects/curator/dashboard.html', {'projects': projects, 'tasks': tasks})

@login_required
@user_passes_test(is_curator)
def assign_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, project__curator=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            # Проверка загрузки разработчика (как в предыдущем коде)
            assigned_dev = form.cleaned_data['assigned_to']
            if assigned_dev:
                from django.db.models import Count, Q
                active_count = Task.objects.filter(
                    assigned_to=assigned_dev,
                    status__in=['new', 'accepted', 'delayed', 'testing', 'rework']
                ).count()
                all_devs = User.objects.filter(profile__role='dev')
                less_loaded = all_devs.annotate(
                    task_count=Count('assigned_tasks', filter=Q(assigned_tasks__status__in=['new', 'accepted', 'delayed', 'testing', 'rework']))
                ).order_by('task_count').first()
                if less_loaded and less_loaded.task_count < active_count:
                    messages.warning(request, f'Разработчик {assigned_dev.username} уже имеет {active_count} активных задач. Менее загружен: {less_loaded.username} (задач: {less_loaded.task_count}).')
            task = form.save()
            # Сохраняем историю назначения
            from tasks.models import TaskAssignmentHistory
            TaskAssignmentHistory.objects.create(
                task=task,
                assigned_to=task.assigned_to,
                assigned_by=request.user
            )
            messages.success(request, 'Задача обновлена.')
            return redirect('curator_dashboard')
    else:
        form = TaskForm(instance=task)
    return render(request, 'projects/curator/assign_task.html', {'form': form, 'task': task})