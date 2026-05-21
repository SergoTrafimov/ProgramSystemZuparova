import pytest
from django.contrib.auth.models import User
from accounts.models import Organization, Profile
from projects.models import Project
from tasks.models import Task
from clients.models import ClientMessage

@pytest.fixture
def org():
    return Organization.objects.create(name="TestOrg", invite_code="123")

@pytest.fixture
def make_user(org):
    def _make_user(username, role, password='pass'):
        user = User.objects.create_user(username=username, password=password)
        profile = user.profile
        profile.role = role
        profile.organization = org
        profile.save()
        return user
    return _make_user

@pytest.fixture
def admin_user(make_user):
    user = make_user('admin', 'admin')
    user.is_superuser = True
    user.is_staff = True
    user.save()
    return user

@pytest.fixture
def analyst(make_user):
    return make_user('analyst', 'analyst')

@pytest.fixture
def curator_user(make_user):
    return make_user('curator', 'curator')

@pytest.fixture
def developer(make_user):
    return make_user('dev', 'dev')

@pytest.fixture
def developer_user(developer):
    return developer

@pytest.fixture
def tester_user(make_user):
    return make_user('tester', 'tester')

@pytest.fixture
def client_user(make_user):
    return make_user('client', 'client')

@pytest.fixture
def project(analyst, org):
    return Project.objects.create(
        name="Test Project",
        description="Test Description",
        created_by=analyst,
        organization=org
    )

@pytest.fixture
def task(project, developer):
    return Task.objects.create(
        project=project,
        title="Test Task",
        description="Task Description",
        status='new',
        assigned_to=developer
    )

@pytest.fixture
def client_message(client_user, project):
    return ClientMessage.objects.create(
        subject="Test Subject",
        message="Test Message",
        created_by=client_user,
        status='new'
    )