# apps/services/models.py
from django.db import models
from apps.general.models import BaseModel
from apps.vehicles.models import Brand, CarModel


class ServiceScope(models.TextChoices):
    ALL = "ALL", "Barcha avtomobillar uchun"
    LIMITED = "LIMITED", "Faqat ayrim (brend/model bo‘yicha)"


class ServiceCategory(BaseModel):
    title = models.CharField(max_length=120, unique=True, verbose_name="Kategoriya nomi")

    class Meta:
        verbose_name = "Xizmat kategoriyasi"
        verbose_name_plural = "Xizmat kategoriyalari"

    def __str__(self):
        return self.title


class Service(BaseModel):
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.PROTECT,
        related_name="services",
        null=True,
        blank=True,
        verbose_name="Kategoriya",
    )
    title = models.CharField(max_length=200, verbose_name="Xizmat nomi")
    price = models.DecimalField(max_digits=14, decimal_places=2, verbose_name="Narxi", default=0)

    scope = models.CharField(
        max_length=20,
        choices=ServiceScope.choices,
        default=ServiceScope.ALL,
        verbose_name="Qamrovi",
    )

    allowed_brands = models.ManyToManyField(
        Brand,
        blank=True,
        related_name="allowed_services",
        verbose_name="Ruxsat berilgan brendlar",
    )
    allowed_models = models.ManyToManyField(
        CarModel,
        blank=True,
        related_name="allowed_services",
        verbose_name="Ruxsat berilgan modellar",
    )

    duration_minutes = models.PositiveIntegerField(null=True, blank=True, verbose_name="Taxminiy davomiyligi (daqiqa)")

    class Meta:
        verbose_name = "Xizmat"
        verbose_name_plural = "Xizmatlar"
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["scope"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.price})"

    def is_allowed_for(self, vehicle) -> bool:
        if self.scope == ServiceScope.ALL:
            return True
        if self.allowed_models.filter(id=vehicle.car_model_id).exists():
            return True
        if self.allowed_brands.filter(id=vehicle.brand_id).exists():
            return True
        return False