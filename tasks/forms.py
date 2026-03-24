from django import forms
from .models import Task
from django.contrib.auth.models import User

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'technical_spec', 'deadline', 'assigned_to']
        widgets = {
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # получаем текущего пользователя
        super().__init__(*args, **kwargs)
        if user and user.profile.role != 'admin' and user.profile.organization:
            self.fields['assigned_to'].queryset = User.objects.filter(
                profile__role='dev',
                profile__organization=user.profile.organization
            )
        else:
            self.fields['assigned_to'].queryset = User.objects.filter(profile__role='dev')