import random
import string
from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    id = models.CharField(max_length=10, primary_key=True, editable=False, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_projects')
    curator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='curated_projects')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.id} - {self.name}"