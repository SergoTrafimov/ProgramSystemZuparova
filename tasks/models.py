from django.db import models
from accounts.models import User
from projects.models import Project

class TaskStatus(models.TextChoices):
    NEW = 'new', 'Новая'
    IN_PROGRESS = 'in_progress', 'В работе'
    TESTING = 'testing', 'На тестировании'
    REWORK = 'rework', 'На доработке'
    DONE = 'done', 'Выполнена'

class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_tasks')
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assigned_tasks'
    )
    status = models.CharField(max_length=20, choices=TaskStatus.choices, default=TaskStatus.NEW)
    deadline = models.DateTimeField()
    priority = models.PositiveSmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent_task = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title

class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return f"Comment by {self.author} on {self.task}"