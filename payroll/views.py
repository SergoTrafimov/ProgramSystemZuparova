from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from datetime import date
from decimal import Decimal, InvalidOperation
from accounts.models import Profile
from .models import Payment

def is_accountant(user):
    return user.is_authenticated and user.profile.role == 'accountant'

@login_required
@user_passes_test(is_accountant)
def accountant_dashboard(request):
    if request.user.profile.role == 'admin':
        profiles = Profile.objects.select_related('user').all()
    else:
        profiles = Profile.objects.select_related('user').filter(
                organization=request.user.profile.organization
            )
    # Получаем все профили, подгружая связанного пользователя
    today = date.today()
    current_period = date(today.year, today.month, 1)

    if request.method == 'POST':
        for profile in profiles:
            # Базовая ставка (если передана)
            salary_base_str = request.POST.get(f'salary_base_{profile.id}')
            if salary_base_str and salary_base_str.strip():
                try:
                    new_salary = Decimal(salary_base_str.strip().replace(',', '.'))
                    if profile.salary_base != new_salary:
                        profile.salary_base = new_salary
                        profile.save()
                except (InvalidOperation, ValueError, TypeError):
                    messages.warning(request, f'Неверное значение ставки для {profile.user.get_full_name()}, пропущено.')

            # Бонус
            bonus_str = request.POST.get(f'bonus_{profile.id}', '0')
            try:
                bonus = Decimal(bonus_str.strip().replace(',', '.')) if bonus_str.strip() else Decimal('0')
            except (InvalidOperation, ValueError, TypeError):
                bonus = Decimal('0')
                messages.warning(request, f'Неверное значение бонуса для {profile.user.get_full_name()}, установлен 0.')

            salary = profile.salary_base
            deductions = salary * Decimal('0.13')
            net = salary + bonus - deductions

            Payment.objects.update_or_create(
                user=profile.user,
                period=current_period,
                defaults={
                    'salary': salary,
                    'bonuses': bonus,
                    'deductions': deductions,
                    'net_salary': net,
                }
            )
        messages.success(request, 'Зарплата рассчитана и сохранена.')
        return redirect('accountant_dashboard')

    # Для каждого профиля подгружаем существующий платёж за период
    for profile in profiles:
        profile.payment = Payment.objects.filter(user=profile.user, period=current_period).first()

    return render(request, 'payroll/dashboard.html', {'profiles': profiles})