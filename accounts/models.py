from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Organization(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Profile(models.Model):
    ROLE_CHOICES = (
        ('dev', 'Разработчик'),
        ('curator', 'Куратор'),
        ('analyst', 'Аналитик'),
        ('tester', 'Тестировщик'),
        ('accountant', 'Бухгалтер'),
        ('admin', 'Администратор'),
        ('client', 'Клиент'),                     # новая роль
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='dev')
    salary_base = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    salary_formula = models.TextField(blank=True)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='profiles',
        verbose_name='Организация'
    )

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"



@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)