from django.db import models
from projects.models import Project

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