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

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'role', 'organization']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Убираем роль 'admin' из выбора
        self.fields['role'].choices = [choice for choice in Profile.ROLE_CHOICES if choice[0] != 'admin']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            profile = user.profile
            profile.role = self.cleaned_data['role']
            profile.organization = self.cleaned_data['organization']
            profile.save()
        return user