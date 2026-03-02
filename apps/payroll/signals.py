# apps/payroll/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from apps.payroll.models import WorkRecord, PayrollMonth, SalaryProfile


def _recalc_month(employee, dt):
    pm, _ = PayrollMonth.objects.get_or_create(
        employee=employee,
        year=dt.year,
        month=dt.month,
    )
    pm.recalc()


@receiver(post_save, sender=WorkRecord)
def workrecord_saved(sender, instance: WorkRecord, **kwargs):
    _recalc_month(instance.employee, instance.performed_at)


@receiver(post_delete, sender=WorkRecord)
def workrecord_deleted(sender, instance: WorkRecord, **kwargs):
    _recalc_month(instance.employee, instance.performed_at)


@receiver(post_save, sender=SalaryProfile)
def salaryprofile_saved(sender, instance: SalaryProfile, **kwargs):
    # SalaryProfile o‘zgarsa — joriy oy qayta hisoblanadi
    from django.utils import timezone
    _recalc_month(instance.employee, timezone.now())