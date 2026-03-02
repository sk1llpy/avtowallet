# apps/users/models.py
from django.db import models
from apps.general.models import BaseModel


class User(BaseModel):
    tg_id = models.CharField(max_length=64, unique=True, verbose_name="Telegram ID")
    tg_username = models.CharField(max_length=255, null=True, blank=True, verbose_name="Telegram username")
    tg_full_name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Telegramdagi to‘liq ism")

    first_name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Ismi")
    last_name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Familiyasi")
    phone_number = models.CharField(max_length=255, verbose_name="Telefon raqami")

    class Meta:
        verbose_name = "Foydalanuvchi (Telegram)"
        verbose_name_plural = "Foydalanuvchilar (Telegram)"

    def __str__(self):
        name = (self.first_name or "").strip()
        last = (self.last_name or "").strip()
        full = f"{name} {last}".strip()
        return f"{full} ({self.phone_number})" if full else f"{self.tg_id} ({self.phone_number})"


class Employee(BaseModel):
    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        related_name="employee_profile",
        verbose_name="Telegram foydalanuvchi",
    )

    position = models.CharField(max_length=120, null=True, blank=True, verbose_name="Lavozimi")
    is_master = models.BooleanField(default=True, verbose_name="Usta (ijrochi)")
    is_manager = models.BooleanField(default=False, verbose_name="Menejer")

    class Meta:
        verbose_name = "Ishchi"
        verbose_name_plural = "Ishchilar"

    def __str__(self):
        return f"Ishchi: {self.user}"