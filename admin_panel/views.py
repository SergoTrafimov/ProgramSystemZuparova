from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from accounts.models import Profile
from projects.models import Project
from tasks.models import Task
from payroll.models import Payment
from django.urls import reverse

def is_admin(user):
    return user.is_authenticated and user.profile.role == 'admin'

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Главная страница админ-панели"""
    users_count = User.objects.count()
    projects_count = Project.objects.count()
    tasks_count = Task.objects.count()
    context = {
        'users_count': users_count,
        'projects_count': projects_count,
        'tasks_count': tasks_count,
    }
    return render(request, 'admin_panel/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def user_list(request):
    users = User.objects.select_related('profile').all()
    return render(request, 'admin_panel/user_list.html', {'users': users})

@login_required
@user_passes_test(is_admin)
def user_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        # Обновление роли
        role = request.POST.get('role')
        if role in dict(Profile.ROLE_CHOICES).keys():
            user.profile.role = role
            user.profile.save()
            messages.success(request, f'Роль пользователя {user.username} обновлена.')
        # Обновление имени и фамилии
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        return redirect('admin_user_list')
    return render(request, 'admin_panel/user_edit.html', {'user': user})

@login_required
@user_passes_test(is_admin)
def project_list(request):
    projects = Project.objects.all()
    return render(request, 'admin_panel/project_list.html', {'projects': projects})

@login_required
@user_passes_test(is_admin)
def project_edit(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        project.name = request.POST.get('name')
        project.description = request.POST.get('description')
        curator_id = request.POST.get('curator')
        if curator_id:
            project.curator = get_object_or_404(User, id=curator_id)
        else:
            project.curator = None
        project.save()
        messages.success(request, f'Проект {project.name} обновлён.')
        return redirect('admin_project_list')
    curators = User.objects.filter(profile__role='curator')
    return render(request, 'admin_panel/project_edit.html', {'project': project, 'curators': curators})

@login_required
@user_passes_test(is_admin)
def project_delete(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        project.delete()
        messages.success(request, f'Проект {project.name} удалён.')
        return redirect('admin_project_list')
    return render(request, 'admin_panel/project_confirm_delete.html', {'project': project})

@login_required
@user_passes_test(is_admin)
def task_list(request):
    tasks = Task.objects.select_related('project', 'assigned_to').all()
    return render(request, 'admin_panel/task_list.html', {'tasks': tasks})

@login_required
@user_passes_test(is_admin)
def task_edit(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        task.title = request.POST.get('title')
        task.description = request.POST.get('description')
        task.technical_spec = request.POST.get('technical_spec')
        task.status = request.POST.get('status')
        assigned_to_id = request.POST.get('assigned_to')
        if assigned_to_id:
            task.assigned_to = get_object_or_404(User, id=assigned_to_id)
        else:
            task.assigned_to = None
        deadline_str = request.POST.get('deadline')
        if deadline_str:
            from django.utils import timezone
            import datetime
            task.deadline = timezone.make_aware(datetime.datetime.fromisoformat(deadline_str))
        else:
            task.deadline = None
        task.save()
        messages.success(request, f'Задача {task.title} обновлена.')
        return redirect('admin_task_list')
    developers = User.objects.filter(profile__role='dev')
    return render(request, 'admin_panel/task_edit.html', {'task': task, 'developers': developers})