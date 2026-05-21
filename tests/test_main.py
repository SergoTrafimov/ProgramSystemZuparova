import pytest
from django.urls import reverse
from projects.models import Project
from tasks.models import Task
from clients.models import ClientMessage, Feedback
from decimal import Decimal
from accounts.forms import RegistrationForm
from django.contrib.auth import get_user_model

User = get_user_model()

# --- Модели ---
@pytest.mark.django_db
def test_create_project(analyst):
    project = Project.objects.create(
        name="Test", description="Desc",
        created_by=analyst, organization=analyst.profile.organization
    )
    assert project.id is not None

# --- Формы ---
@pytest.mark.django_db
def test_registration_requires_invite_code_for_non_client(org):
    form = RegistrationForm(data={
        'username': 'dev', 'first_name': 'Dev', 'last_name': 'User',
        'password1': 'strongpass', 'password2': 'strongpass',
        'role': 'dev', 'organization': org.id, 'invite_code': ''
    })
    assert not form.is_valid()
    errors = form.errors
    # Ошибка может быть в __all__ или в поле invite_code
    assert 'invite_code' in errors or any('код приглашения' in str(err) for err in errors.get('__all__', []))

@pytest.mark.django_db
def test_registration_with_correct_invite_code(org):
    form = RegistrationForm(data={
        'username': 'dev2', 'first_name': 'Dev', 'last_name': 'Two',
        'password1': 'strongpass', 'password2': 'strongpass',
        'role': 'dev', 'organization': org.id, 'invite_code': '123'
    })
    assert form.is_valid()
    user = form.save()
    assert user.profile.role == 'dev'

# --- Представления аналитика ---
@pytest.mark.django_db
def test_analyst_dashboard(client, analyst, project):
    client.force_login(analyst)
    url = reverse('analyst_dashboard')
    response = client.get(url)
    assert response.status_code == 200
    assert project in response.context['projects']

@pytest.mark.django_db
def test_create_project_with_tasks(client, analyst):
    client.force_login(analyst)
    url = reverse('create_project')
    data = {
        'name': 'New Project',
        'description': 'Desc',
        'tasks_text': 'Task1\nTask2'
    }
    response = client.post(url, data)
    assert response.status_code == 302
    project = Project.objects.get(name='New Project')
    assert Task.objects.filter(project=project).count() == 2

@pytest.mark.django_db
def test_analyst_messages(client, analyst, client_message):
    client.force_login(analyst)
    url = reverse('analyst_messages')
    response = client.get(url)
    assert response.status_code == 200
    assert client_message in response.context['messages']

# --- Представления куратора ---
@pytest.mark.django_db
def test_curator_dashboard(client, curator_user, project, task):
    client.force_login(curator_user)
    project.curator = curator_user
    project.save()
    url = reverse('curator_dashboard')
    response = client.get(url)
    assert response.status_code == 200
    assert project in response.context['projects']
    assert task in response.context['tasks']

@pytest.mark.django_db
def test_assign_task(client, curator_user, task, developer_user):
    client.force_login(curator_user)
    task.project.curator = curator_user
    task.project.save()
    url = reverse('assign_task', args=[task.id])
    data = {
        'assigned_to': developer_user.id,
        'deadline': '2025-12-31 23:59',
        'title': task.title,
        'description': task.description,
    }
    response = client.post(url, data)
    assert response.status_code == 302
    task.refresh_from_db()
    assert task.assigned_to == developer_user

# --- Представления разработчика ---
@pytest.mark.django_db
def test_developer_dashboard(client, developer, task):
    client.force_login(developer)
    task.assigned_to = developer
    task.save()
    url = reverse('developer_dashboard')
    response = client.get(url)
    assert response.status_code == 200
    assert task in response.context['tasks']

@pytest.mark.django_db
def test_developer_can_accept_task(client, developer):
    client.force_login(developer)
    project = Project.objects.create(name="P", description="D", created_by=developer, organization=developer.profile.organization)
    task = Task.objects.create(project=project, title="T", status='new', assigned_to=developer)
    url = reverse('update_task_status', args=[task.id, 'accepted'])
    client.get(url)
    task.refresh_from_db()
    assert task.status == 'accepted'

@pytest.mark.django_db
def test_developer_can_delay_task(client, developer):
    client.force_login(developer)
    project = Project.objects.create(name="P", description="D", created_by=developer, organization=developer.profile.organization)
    task = Task.objects.create(project=project, title="T", status='new', assigned_to=developer)
    url = reverse('update_task_status', args=[task.id, 'delayed'])
    client.get(url)
    task.refresh_from_db()
    assert task.status == 'delayed'

@pytest.mark.django_db
def test_developer_can_mark_done(client, developer):
    client.force_login(developer)
    project = Project.objects.create(name="P", description="D", created_by=developer, organization=developer.profile.organization)
    task = Task.objects.create(project=project, title="T", status='accepted', assigned_to=developer)
    url = reverse('update_task_status', args=[task.id, 'done'])
    client.get(url)
    task.refresh_from_db()
    assert task.status == 'testing'

# --- Представления тестировщика ---
@pytest.mark.django_db
def test_tester_dashboard(client, tester_user, task):
    client.force_login(tester_user)
    task.status = 'testing'
    task.save()
    url = reverse('tester_dashboard')
    response = client.get(url)
    assert response.status_code == 200
    # В зависимости от вашего представления, переменная может называться 'tasks'
    assert 'tasks' in response.context
    assert task in response.context['tasks']

@pytest.mark.django_db
def test_tester_approve_task(client, tester_user, task):
    client.force_login(tester_user)
    task.status = 'testing'
    task.save()
    url = reverse('test_task', args=[task.id])
    response = client.post(url, {'action': 'approve'})
    assert response.status_code == 302
    task.refresh_from_db()
    assert task.status == 'completed'

# --- Представления бухгалтера ---
@pytest.mark.django_db
def test_accountant_calculates_salary(client, make_user):
    accountant = make_user('acc', 'accountant')
    dev = make_user('dev2', 'dev')
    dev.profile.salary_base = Decimal('50000')
    dev.profile.save()
    client.force_login(accountant)
    url = reverse('accountant_dashboard')
    data = {f'salary_base_{dev.profile.id}': '50000', f'bonus_{dev.profile.id}': '0'}
    response = client.post(url, data)
    assert response.status_code == 302
    from payroll.models import Payment
    payment = Payment.objects.get(user=dev)
    assert payment.net_salary == Decimal('43500')

# --- Клиент и аналитик: обращения ---
@pytest.mark.django_db
def test_client_message_flow(client, client_user, analyst):
    client.force_login(client_user)
    url = reverse('create_client_message')
    client.post(url, {'subject': 'Help', 'message': 'Problem'})
    msg = ClientMessage.objects.get(subject='Help')
    assert msg.status == 'new'

    client.force_login(analyst)
    reply_url = reverse('view_message', args=[msg.id])
    client.post(reply_url, {'text': 'We will help'})
    msg.refresh_from_db()
    assert msg.status == 'processing'
    assert msg.replies.count() == 1
    reply = msg.replies.first()
    assert reply.text == 'We will help'
    assert reply.author == analyst

# --- Обратная связь по проекту ---
@pytest.mark.django_db
def test_project_feedback(client, analyst, project):
    client.force_login(analyst)
    url = reverse('project_feedback', args=[project.id])
    response = client.post(url, {'message': 'Test feedback'})
    assert response.status_code == 302
    feedback = Feedback.objects.filter(project=project, message='Test feedback').first()
    assert feedback is not None
    assert feedback.from_client is False  # аналитик — не клиент

# --- Создание проекта из обращения ---
@pytest.mark.django_db
def test_create_project_from_message(client, analyst, client_message):
    client.force_login(analyst)
    url = reverse('create_project_from_message', args=[client_message.id])
    data = {
        'name': 'Project from message',
        'description': 'Desc',
    }
    response = client.post(url, data)
    assert response.status_code == 302
    client_message.refresh_from_db()
    assert client_message.project is not None
    assert client_message.project.name == 'Project from message'

# --- Диалог проекта ---
@pytest.mark.django_db
def test_project_dialog(client, analyst, project, client_message):
    client.force_login(analyst)
    client_message.project = project
    client_message.save()
    url = reverse('project_dialog', args=[project.id])
    response = client.get(url)
    assert response.status_code == 200
    assert client_message in response.context['messages']


# Тест для списка уведомлений
@pytest.mark.django_db
def test_notification_list(client, developer):
    client.force_login(developer)
    response = client.get(reverse('notification_list'))
    assert response.status_code == 200
@pytest.mark.django_db
def test_admin_dashboard(client, admin_user):
    client.force_login(admin_user)
    response = client.get(reverse('admin_dashboard'))
    assert response.status_code == 200

@pytest.mark.django_db
def test_analyst_can_close_message(client, analyst, client_message):
    client.force_login(analyst)
    url = reverse('close_message', args=[client_message.id])
    response = client.get(url)
    assert response.status_code == 302
    client_message.refresh_from_db()
    assert client_message.status == 'resolved'

@pytest.mark.django_db
def test_admin_project_list(client, admin_user, project):
    client.force_login(admin_user)
    url = reverse('admin_project_list')
    response = client.get(url)
    assert response.status_code == 200
    assert project in response.context['projects']
@pytest.mark.django_db
def test_analyst_can_view_project_tasks(client, analyst, project, task):
    client.force_login(analyst)
    url = reverse('project_tasks', args=[project.id])
    response = client.get(url)
    assert response.status_code == 200
    assert task in response.context['tasks']

@pytest.mark.django_db
def test_developer_can_update_repository_url(client, developer, task):
    client.force_login(developer)
    task.assigned_to = developer
    task.save()
    url = reverse('update_task_repo', args=[task.id])
    response = client.post(url, {'repository_url': 'https://github.com/test/repo'})
    assert response.status_code == 302
    task.refresh_from_db()
    assert task.repository_url == 'https://github.com/test/repo'

@pytest.mark.django_db
def test_client_can_view_own_messages(client, client_user, client_message):
    client.force_login(client_user)
    url = reverse('view_client_message', args=[client_message.id])
    response = client.get(url)
    assert response.status_code == 200

@pytest.mark.django_db
def test_analyst_can_create_project_without_message(client, analyst):
    client.force_login(analyst)
    url = reverse('create_project')
    data = {
        'name': 'Project No Message',
        'description': 'Desc',
        'tasks_text': 'Task1'
    }
    response = client.post(url, data)
    assert response.status_code == 302
    assert Project.objects.filter(name='Project No Message').exists()