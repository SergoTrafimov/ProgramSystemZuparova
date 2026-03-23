from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db import models

class Role(models.TextChoices):
    DEVELOPER = 'dev', 'Разработчик'
    CURATOR = 'cur', 'Куратор'
    ANALYST = 'ana', 'Аналитик'
    TESTER = 'tst', 'Тестировщик'
    ACCOUNTANT = 'acc', 'Бухгалтерия'

class User(AbstractUser):
    role = models.CharField(max_length=3, choices=Role.choices, blank=True, null=True)
    # добавьте другие поля по необходимости
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
