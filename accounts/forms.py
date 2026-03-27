from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Organization

class RegistrationForm(UserCreationForm):
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES, required=True, label='Роль')
    first_name = forms.CharField(max_length=30, required=True, label='Имя')
    last_name = forms.CharField(max_length=30, required=True, label='Фамилия')
    organization = forms.ModelChoiceField(
        queryset=Organization.objects.all(),
        required=True,
        label='Организация',
        empty_label='Выберите организацию'
    )
    invite_code = forms.CharField(max_length=50, required=False, label='Код приглашения (для ролей, кроме клиента)')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'role', 'organization', 'invite_code']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Убираем роль 'admin' из выбора
        self.fields['role'].choices = [choice for choice in Profile.ROLE_CHOICES if choice[0] != 'admin']

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        organization = cleaned_data.get('organization')
        invite_code = cleaned_data.get('invite_code')

        # Если роль не клиент, проверяем код
        if role and role != 'client':
            if not invite_code:
                raise forms.ValidationError('Для выбранной роли требуется код приглашения.')
            if not organization or organization.invite_code != invite_code:
                raise forms.ValidationError('Неверный код приглашения для выбранной организации.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            # Обновляем или создаём профиль
            profile = user.profile
            profile.role = self.cleaned_data['role']
            profile.organization = self.cleaned_data['organization']
            profile.save()
        return user