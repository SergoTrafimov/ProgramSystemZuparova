import random
import string
from django.db import models
from accounts.models import User, Role

def generate_project_id():
    while True:
        code = 'PRJ-' + ''.join(random.choices(string.digits, k=6))
        if not Project.objects.filter(project_id=code).exists():
            return code

class Project(models.Model):
    project_id = models.CharField(max_length=10, unique=True, default=generate_project_id)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    curator = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        limit_choices_to={'role': Role.CURATOR},
        related_name='curated_projects'
    )
    clients = models.ManyToManyField('clients.Client', related_name='projects')
    testers = models.ManyToManyField(
        User, limit_choices_to={'role': Role.TESTER},
        related_name='testing_projects', blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.project_id} - {self.name}"