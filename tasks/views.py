from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from .models import Task

def is_developer(user):
    return user.is_authenticated and user.profile.role == 'dev'

def is_tester(user):
    return user.is_authenticated and user.profile.role == 'tester'

@login_required
@user_passes_test(is_developer)
def developer_dashboard(request):
    if request.user.profile.role == 'admin':
        tasks = Task.objects.filter(assigned_to=request.user).exclude(status='completed')
    else:
        tasks = Task.objects.filter(
            assigned_to=request.user,
            project__organization=request.user.profile.organization
        ).exclude(status='completed')
    tasks = Task.objects.filter(assigned_to=request.user).exclude(status='completed')
    now = timezone.now()
    for task in tasks:
        if task.deadline and task.deadline < now:
            messages.warning(request, f'Просрочена задача: {task.title}')
        elif task.deadline and (task.deadline - now).days <= 1:
            messages.info(request, f'Скоро дедлайн: {task.title}')
    return render(request, 'tasks/developer/dashboard.html', {'tasks': tasks})

@login_required
@user_passes_test(is_developer)
def update_task_status(request, task_id, status):
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)
    allowed = ['accepted', 'delayed', 'done']
    allowed = ['accepted', 'delayed', 'done']
    if status not in allowed:
        messages.error(request, 'Недопустимый статус.')
        return redirect('developer_dashboard')

    if status == 'done':
        task.status = 'testing'
    else:
        task.status = status
    task.save()
    messages.success(request, f'Статус задачи изменён на {task.get_status_display()}.')
    return redirect('developer_dashboard')

@login_required
@user_passes_test(is_tester)
def tester_dashboard(request):
    if request.user.profile.role == 'admin':
        tasks = Task.objects.filter(status__in=['testing', 'rework'])
    else:
        tasks = Task.objects.filter(
            status__in=['testing', 'rework'],
            project__organization=request.user.profile.organization
        )
    return render(request, 'tasks/tester/dashboard.html', {'tasks': tasks})

@login_required
@user_passes_test(is_tester)
def test_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, status__in=['testing', 'rework'])
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            task.status = 'completed'
            messages.success(request, 'Задача принята.')
        elif action == 'rework':
            task.status = 'rework'
            task.tester_comment = request.POST.get('comment', '')
            messages.warning(request, 'Задача отправлена на доработку.')
        task.save()
        return redirect('tester_dashboard')
    return render(request, 'tasks/tester/test_task.html', {'task': task})

@login_required
@user_passes_test(is_developer)
def update_repository_url(request, task_id):
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)
    if request.method == 'POST':
        repo_url = request.POST.get('repository_url', '').strip()
        task.repository_url = repo_url
        task.save()
        messages.success(request, 'Ссылка на репозиторий сохранена.')
    return redirect('developer_dashboard')