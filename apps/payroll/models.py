# apps/payroll/models.py
from decimal import Decimal
from django.db import models
from django.utils import timezone

from apps.general.models import BaseModel
from apps.users.models import Employee


class SalaryProfile(BaseModel):
    employee = models.OneToOneField(
        Employee,
        on_delete=models.CASCADE,
        related_name="salary_profile",
        verbose_name="Ishchi",
    )
    fixed_salary = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name="Fiks oylik maosh",
    )
    kpi_percent = models.PositiveIntegerField(default=10, verbose_name="KPI foizi (standart)")

    class Meta:
        verbose_name = "Maosh sozlamasi"
        verbose_name_plural = "Maosh sozlamalari"

    def __str__(self):
        return f"{self.employee} | fiks={self.fixed_salary} | KPI={self.kpi_percent}%"


class WorkRecord(BaseModel):
    """
    Har bir yakunlangan booking = ishchiga ish yozuvi.
    KPI = amount * (kpi_percent / 100)
    """
    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name="work_records",
        verbose_name="Ishchi",
    )
    booking = models.OneToOneField(
        "bookings.Booking",
        on_delete=models.PROTECT,
        related_name="work_record",
        verbose_name="Booking",
    )

    amount = models.DecimalField(max_digits=14, decimal_places=2, verbose_name="Ish summasi")
    kpi_percent = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="KPI foizi (shu ish uchun)",
        help_text="Bo‘sh bo‘lsa SalaryProfile’dan olinadi.",
    )
    kpi_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="KPI summasi",
    )

    performed_at = models.DateTimeField(default=timezone.now, verbose_name="Bajarilgan vaqti")

    class Meta:
        verbose_name = "Ish yozuvi"
        verbose_name_plural = "Ish yozuvlari"
        indexes = [models.Index(fields=["performed_at"])]

    def save(self, *args, **kwargs):
        # KPI foizni auto olish
        if not self.kpi_percent:
            sp = getattr(self.employee, "salary_profile", None)
            self.kpi_percent = sp.kpi_percent if sp else 10

        self.kpi_amount = (self.amount * Decimal(self.kpi_percent)) / Decimal("100")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee} | ish={self.amount} | KPI={self.kpi_amount}"


class PayrollMonth(BaseModel):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name="payroll_months",
        verbose_name="Ishchi",
    )
    year = models.PositiveIntegerField(verbose_name="Yil")
    month = models.PositiveIntegerField(verbose_name="Oy")

    fixed_salary_snapshot = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name="Fiks oylik (snapshot)",
    )
    works_total = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name="Oy bo‘yicha ishlar summasi",
    )
    kpi_total = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name="Oy bo‘yicha KPI summasi",
    )
    total_salary = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name="Jami oylik (fiks + KPI)",
    )

    class Meta:
        verbose_name = "Oylik hisob"
        verbose_name_plural = "Oylik hisoblar"
        constraints = [
            models.UniqueConstraint(fields=["employee", "year", "month"], name="uniq_employee_year_month")
        ]

    def __str__(self):
        return f"{self.employee} {self.year}-{self.month:02d} = {self.total_salary}"

    def recalc(self, save: bool = True):
        """
        Shu oy bo‘yicha WorkRecordlarni yig‘ib, jami oylikni qayta hisoblaydi.
        """
        sp = getattr(self.employee, "salary_profile", None)
        self.fixed_salary_snapshot = sp.fixed_salary if sp else Decimal("0")

        qs = self.employee.work_records.filter(performed_at__year=self.year, performed_at__month=self.month)

        works_total = Decimal("0")
        kpi_total = Decimal("0")
        for wr in qs:
            works_total += (wr.amount or Decimal("0"))
            kpi_total += (wr.kpi_amount or Decimal("0"))

        self.works_total = works_total
        self.kpi_total = kpi_total
        self.total_salary = self.fixed_salary_snapshot + self.kpi_total

        if save:
            self.save()
        return self