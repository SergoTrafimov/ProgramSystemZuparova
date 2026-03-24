from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Task, TaskStatus
from accounts.models import Role
from django.db.models import Count, Q

@receiver(pre_save, sender=Task)
def auto_assign_tester(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = Task.objects.get(pk=instance.pk)
        except Task.DoesNotExist:
            return
        if old.status != TaskStatus.TESTING and instance.status == TaskStatus.TESTING:
            # Задача перешла в тестирование – назначаем тестировщика
            project = instance.project
            testers = project.testers.all()
            if testers.exists():
                # Подсчёт активных задач у каждого тестировщика
                tester_load = {}
                for tester in testers:
                    count = Task.objects.filter(
                        assigned_to=tester,
                        status__in=[TaskStatus.TESTING, TaskStatus.REWORK]
                    ).count()
                    tester_load[tester.id] = count
                best_tester_id = min(tester_load, key=tester_load.get)
                instance.assigned_to_id = best_tester_id
            # Если нет тестировщиков – оставляем без назначения (куратор назначит вручную)