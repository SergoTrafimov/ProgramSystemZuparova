from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile

# Если вы хотите добавить профиль в админку, можно создать inline
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'

# Расширяем стандартный UserAdmin, добавляя inline профиля
class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline]

# Отменяем стандартную регистрацию и регистрируем кастомную
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Если вы хотите отдельно зарегистрировать Profile, тоже можно
admin.site.register(Profile)