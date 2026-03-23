from django.core.management.base import BaseCommand
from django.utils import timezone
from tasks.models import Task
from notifications.models import Notification

class Command(BaseCommand):
    help = 'Проверяет дедлайны и создаёт уведомления'

    def handle(self, *args, **options):
        now = timezone.now()
        upcoming = Task.objects.filter(
            deadline__gt=now,
            deadline__lte=now + timezone.timedelta(days=1),
            status__in=['new', 'accepted']
        )
        for task in upcoming:
            if task.assigned_to:
                Notification.objects.get_or_create(
                    user=task.assigned_to,
                    task=task,
                    defaults={'message': f'Дедлайн задачи "{task.title}" наступает {task.deadline}'}
                )
        overdue = Task.objects.filter(
            deadline__lt=now,
            status__in=['new', 'accepted']
        )
        for task in overdue:
            if task.assigned_to:
                Notification.objects.get_or_create(
                    user=task.assigned_to,
                    task=task,
                    defaults={'message': f'Задача "{task.title}" просрочена!'}
                )
        self.stdout.write('Уведомления созданы')