from django.db import models
from accounts.models import User

class SalaryRule(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='salary_rule')
    base_salary = models.DecimalField(max_digits=10, decimal_places=2)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    bonus_per_task = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def __str__(self):
        return f"Salary rule for {self.user}"

class Payroll(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payrolls')
    period_start = models.DateField()
    period_end = models.DateField()
    base_amount = models.DecimalField(max_digits=10, decimal_places=2)
    additional_params = models.JSONField(default=dict)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Payroll for {self.user} ({self.period_start} - {self.period_end})"