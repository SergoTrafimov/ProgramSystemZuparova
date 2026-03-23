from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Project
from accounts.models import Profile
from django.contrib.auth.models import User
import random

@receiver(post_save, sender=Project)
def assign_curator(sender, instance, created, **kwargs):
    if created and not instance.curator:
        curators = User.objects.filter(profile__role='curator')
        if curators.exists():
            instance.curator = random.choice(curators)
            instance.save()