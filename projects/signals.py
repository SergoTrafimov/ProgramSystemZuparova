from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Project
from accounts.models import User, Role

@receiver(post_save, sender=Project)
def assign_curator(sender, instance, created, **kwargs):
    if created and not instance.curator:
        # Найти куратора с наименьшим числом активных проектов
        curators = User.objects.filter(role=Role.CURATOR, is_active=True)
        if curators.exists():
            # Аннотируем количеством проектов (активных)
            from django.db.models import Count
            curators = curators.annotate(project_count=Count('curated_projects', filter=models.Q(curated_projects__active=True)))
            curator = curators.order_by('project_count').first()
            instance.curator = curator
            instance.save(update_fields=['curator'])