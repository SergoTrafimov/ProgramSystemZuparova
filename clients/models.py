from django.db import models
from projects.models import Project
from django.contrib.auth.models import User

class Client(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name

class Feedback(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='feedbacks')
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)
    message = models.TextField()
    from_client = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    responded = models.BooleanField(default=False)

    def __str__(self):
        return f"Feedback for {self.project.id}"

class ClientMessage(models.Model):
    STATUS_CHOICES = (
        ('new', 'Новое'),
        ('processing', 'В обработке'),
        ('resolved', 'Решено'),
    )
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client_messages')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='assigned_messages')
    project = models.ForeignKey('projects.Project', on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='client_messages')

    def __str__(self):
        return f"{self.subject} - {self.created_by}"

class MessageReply(models.Model):
    message = models.ForeignKey(ClientMessage, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply to {self.message.subject} by {self.author.username}"