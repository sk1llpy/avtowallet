# apps/bookings/models.py
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from django.utils import timezone

from apps.general.models import BaseModel
from apps.users.models import User, Employee
from apps.vehicles.models import Vehicle
from apps.services.models import Service


class BookingStatus(models.TextChoices):
    PENDING = "PENDING", "Kutilmoqda"
    CONFIRMED = "CONFIRMED", "Tasdiqlandi"
    IN_PROGRESS = "IN_PROGRESS", "Jarayonda"
    COMPLETED = "COMPLETED", "Bajarildi"
    CANCELLED = "CANCELLED", "Bekor qilindi"


class Booking(BaseModel):
    client = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="bookings",
        verbose_name="Mijoz (Telegram foydalanuvchi)",
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.PROTECT,
        related_name="bookings",
        verbose_name="Avtomobil",
    )

    booking_date = models.DateField(verbose_name="Bron sanasi")
    booking_time = models.TimeField(verbose_name="Bron vaqti")

    status = models.CharField(
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING,
        verbose_name="Holati",
    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name="assigned_bookings",
        null=True,
        blank=True,
        verbose_name="Ijrochi ishchi",
    )

    note = models.TextField(null=True, blank=True, verbose_name="Izoh")

    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Yakunlangan vaqti")
    total_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Jami summa",
    )

    class Meta:
        verbose_name = "Bron (Booking)"
        verbose_name_plural = "Bronlar (Bookinglar)"
        indexes = [
            models.Index(fields=["booking_date", "booking_time"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"#{self.id} {self.client} {self.booking_date} {self.booking_time}"

    def clean(self):
        # oddiy validatsiya (xohlasangiz kuchaytiramiz)
        if self.status == BookingStatus.COMPLETED and not self.completed_at:
            raise ValidationError("COMPLETED bo‘lsa, completed_at bo‘lishi kerak.")

    def recalc_total(self, save: bool = True) -> Decimal:
        """
        BookingService line laridan jami summani avtomatik hisoblaydi.
        """
        amount_expr = ExpressionWrapper(
            F("price") * F("qty"),
            output_field=DecimalField(max_digits=14, decimal_places=2),
        )
        total = (
            self.booking_services.aggregate(s=Sum(amount_expr)).get("s")
            or Decimal("0")
        )

        self.total_amount = total
        if save:
            self.save(update_fields=["total_amount", "updated_at"])
        return total

    @transaction.atomic
    def complete(self, employee: Employee):
        """
        Bookingni COMPLETED qiladi.
        - total_amount booking_services dan hisoblanadi
        - WorkRecord yaratadi/yangi qiymatga moslaydi
        - PayrollMonth avtomatik recalc bo‘ladi (signal orqali)
        """
        from apps.payroll.models import WorkRecord

        if self.status in (BookingStatus.CANCELLED, BookingStatus.COMPLETED):
            return self

        if not employee:
            raise ValidationError("Yakunlash uchun employee tanlanishi shart.")

        # xizmatlar mosligini tekshirish
        for line in self.booking_services.select_related("service"):
            srv: Service = line.service
            if not srv.is_allowed_for(self.vehicle):
                raise ValidationError(f"Bu xizmat ushbu avtomobilga mos emas: {srv}")

        self.employee = employee
        total = self.recalc_total(save=False)

        self.status = BookingStatus.COMPLETED
        self.completed_at = timezone.now()
        self.total_amount = total
        self.save()

        # WorkRecord: booking uchun 1 ta yozuv bo‘lishi kerak
        WorkRecord.objects.update_or_create(
            booking=self,
            defaults={
                "employee": employee,
                "amount": total,
            },
        )

        return self


class BookingService(BaseModel):
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name="booking_services",
        verbose_name="Bron (Booking)",
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        related_name="booking_lines",
        verbose_name="Xizmat",
    )

    qty = models.PositiveIntegerField(default=1, verbose_name="Soni (qty)")

    price = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Narxi",
        help_text="Bo‘sh qoldirilsa, Service.price avtomatik qo‘yiladi.",
    )

    class Meta:
        verbose_name = "Bron xizmati"
        verbose_name_plural = "Bron xizmatlari"

    def __str__(self):
        return f"{self.booking_id}: {self.service.title}"

    def clean(self):
        if self.qty < 1:
            raise ValidationError("qty kamida 1 bo‘lishi kerak.")

    def save(self, *args, **kwargs):
        # default price = service.price (lekin keyin o‘zgartirsa bo‘ladi)
        if self.price is None and self.service_id:
            self.price = self.service.price or Decimal("0")
        super().save(*args, **kwargs)