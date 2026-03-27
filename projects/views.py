from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Project
from .forms import ProjectForm
from tasks.models import Task
from tasks.forms import TaskForm
from clients.models import ClientMessage
from clients.forms import ClientMessageForm, MessageReplyForm

def is_analyst(user):
    return user.is_authenticated and user.profile.role == 'analyst'

def is_curator(user):
    return user.is_authenticated and user.profile.role == 'curator'

def is_developer(user):
    return user.is_authenticated and user.profile.role == 'dev'

def is_tester(user):
    return user.is_authenticated and user.profile.role == 'tester'

def is_accountant(user):
    return user.is_authenticated and user.profile.role == 'accountant'

@login_required
def index(request):
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
    projects = Project.objects.filter(
        created_by=request.user,
        organization=request.user.profile.organization
    )
    return render(request, 'projects/analyst/dashboard.html', {'projects': projects})

@login_required
@user_passes_test(is_analyst)
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, user=request.user)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.organization = request.user.profile.organization
            project.save()

            client_message = form.cleaned_data.get('client_message')
            if client_message:
                client_message.project = project
                client_message.status = 'processing'
                client_message.save()
                messages.success(request, f'Обращение "{client_message.subject}" привязано к проекту.')

            tasks_text = form.cleaned_data.get('tasks_text', '')
            if tasks_text:
                task_names = [line.strip() for line in tasks_text.split('\n') if line.strip()]
                for name in task_names:
                    Task.objects.create(
                        project=project,
                        title=name,
                        description='Базовая задача, созданная аналитиком',
                        created_by=request.user,
                        status='new'
                    )
                messages.success(request, f'Создано {len(task_names)} задач.')
            else:
                messages.success(request, 'Проект создан без задач.')

            return redirect('analyst_dashboard')
    else:
        form = ProjectForm(user=request.user)
    return render(request, 'projects/analyst/create_project.html', {'form': form})

@login_required
@user_passes_test(is_analyst)
def analyst_messages(request):
    # Показываем все обращения, которые не закрыты (new/processing) и принадлежат организации аналитика
    messages_list = ClientMessage.objects.filter(
        status__in=['new', 'processing'],
        created_by__profile__organization=request.user.profile.organization
    ).order_by('-created_at')
    return render(request, 'projects/analyst/messages.html', {'messages': messages_list})

@login_required
@user_passes_test(is_analyst)
def view_message(request, message_id):
    message = get_object_or_404(ClientMessage, id=message_id)
    # Проверка: аналитик видит только обращения своей организации
    if message.created_by.profile.organization != request.user.profile.organization:
        messages.error(request, 'Доступ запрещён')
        return redirect('analyst_messages')
    if request.method == 'POST':
        form = MessageReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.message = message
            reply.author = request.user
            reply.save()
            if message.status == 'new':
                message.status = 'processing'
                message.save()
            messages.success(request, 'Ответ отправлен.')
            return redirect('view_message', message_id=message.id)
    else:
        form = MessageReplyForm()
    replies = message.replies.all().order_by('created_at')
    return render(request, 'projects/analyst/view_message.html', {
        'message': message,
        'replies': replies,
        'form': form,
    })

@login_required
@user_passes_test(is_analyst)
def close_message(request, message_id):
    message = get_object_or_404(ClientMessage, id=message_id)
    if message.created_by.profile.organization != request.user.profile.organization:
        messages.error(request, 'Доступ запрещён')
        return redirect('analyst_messages')
    message.status = 'resolved'
    message.save()
    messages.success(request, 'Обращение закрыто.')
    return redirect('analyst_messages')

@login_required
@user_passes_test(is_analyst)
def create_project_from_message(request, message_id):
    message = get_object_or_404(ClientMessage, id=message_id, project__isnull=True)
    if message.created_by.profile.organization != request.user.profile.organization:
        messages.error(request, 'Доступ запрещён')
        return redirect('analyst_messages')
    if request.method == 'POST':
        form = ProjectForm(request.POST, user=request.user)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.organization = request.user.profile.organization
            project.save()
            message.project = project
            message.status = 'processing'
            message.save()
            messages.success(request, f'Проект "{project.name}" создан и связан с обращением.')
            return redirect('project_dialog', project_id=project.id)
    else:
        initial = {
            'name': message.subject,
            'description': message.message,
        }
        form = ProjectForm(initial=initial, user=request.user)
        form.fields.pop('client_message', None)
    return render(request, 'projects/analyst/create_project_from_message.html', {
        'form': form,
        'message': message,
    })

@login_required
def project_dialog(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    # Проверка доступа
    if request.user.profile.role == 'client':
        # Клиент может видеть проект, если он его создатель ИЛИ проект связан с его обращением
        if request.user != project.created_by and not project.client_messages.filter(created_by=request.user).exists():
            messages.error(request, 'Доступ запрещён')
            return redirect('index')
    elif request.user.profile.role == 'analyst':
        if request.user != project.created_by:
            messages.error(request, 'Вы не являетесь аналитиком этого проекта')
            return redirect('index')
    else:
        messages.error(request, 'У вас нет прав для просмотра диалога')
        return redirect('index')

    messages_list = ClientMessage.objects.filter(project=project).order_by('created_at')
    if request.method == 'POST':
        form = ClientMessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.created_by = request.user
            msg.project = project
            if request.user.profile.role == 'client':
                msg.status = 'new'
            else:
                msg.status = 'processing'
            msg.save()
            messages.success(request, 'Сообщение отправлено')
            return redirect('project_dialog', project_id=project.id)
    else:
        form = ClientMessageForm()
    return render(request, 'projects/dialog.html', {
        'project': project,
        'messages': messages_list,
        'form': form,
    })

@login_required
def project_tasks(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    tasks = Task.objects.filter(project=project)
    return render(request, 'projects/project_tasks.html', {'project': project, 'tasks': tasks})

@login_required
@user_passes_test(is_curator)
def curator_dashboard(request):
    projects = Project.objects.filter(
        curator=request.user,
        organization=request.user.profile.organization
    )
    tasks = Task.objects.filter(
        project__curator=request.user,
        project__organization=request.user.profile.organization
    ).exclude(status='completed')
    return render(request, 'projects/curator/dashboard.html', {'projects': projects, 'tasks': tasks})

@login_required
@user_passes_test(is_curator)
def assign_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, project__curator=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, user=request.user)
        if form.is_valid():
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
            from tasks.models import TaskAssignmentHistory
            TaskAssignmentHistory.objects.create(
                task=task,
                assigned_to=task.assigned_to,
                assigned_by=request.user
            )
            messages.success(request, 'Задача обновлена.')
            return redirect('curator_dashboard')
    else:
        form = TaskForm(instance=task, user=request.user)
    return render(request, 'projects/curator/assign_task.html', {'form': form, 'task': task})