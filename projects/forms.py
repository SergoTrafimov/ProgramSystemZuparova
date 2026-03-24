from django import forms
from .models import Project
from clients.models import ClientMessage

class ProjectForm(forms.ModelForm):
    tasks_text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5}),
        required=False,
        label='Базовые задачи (по одной на строке)',
        help_text='Введите названия задач, которые будут созданы автоматически.'
    )
    client_message = forms.ModelChoiceField(
        queryset=ClientMessage.objects.none(),
        required=False,
        label='Связанное обращение клиента'
    )

    class Meta:
        model = Project
        fields = ['name', 'description', 'tasks_text', 'client_message']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Администратор видит все обращения без проекта, со статусом new/processing
            if user.profile.role == 'admin':
                qs = ClientMessage.objects.filter(
                    status__in=['new', 'processing'],
                    project__isnull=True
                ).order_by('-created_at')
            # Аналитик видит обращения своей организации
            elif user.profile.role == 'analyst':
                qs = ClientMessage.objects.filter(
                    status__in=['new', 'processing'],
                    project__isnull=True,
                    created_by__profile__organization=user.profile.organization
                ).order_by('-created_at')
            else:
                qs = ClientMessage.objects.none()
            self.fields['client_message'].queryset = qs