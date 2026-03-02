# apps/vehicles/models.py
from django.db import models
from apps.general.models import BaseModel
from apps.users.models import User


class Brand(BaseModel):
    name = models.CharField(max_length=120, unique=True, verbose_name="Brend nomi")

    class Meta:
        verbose_name = "Brend"
        verbose_name_plural = "Brendlar"

    def __str__(self):
        return self.name


class CarModel(BaseModel):
    brand = models.ForeignKey(
        Brand,
        on_delete=models.PROTECT,
        related_name="models",
        verbose_name="Brend",
    )
    name = models.CharField(max_length=120, verbose_name="Model nomi")

    class Meta:
        verbose_name = "Avtomobil modeli"
        verbose_name_plural = "Avtomobil modellari"
        constraints = [
            models.UniqueConstraint(fields=["brand", "name"], name="uniq_brand_model_name")
        ]

    def __str__(self):
        return f"{self.brand.name} {self.name}"


class Vehicle(BaseModel):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="vehicles",
        verbose_name="Egasi (Telegram foydalanuvchi)",
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.PROTECT,
        related_name="vehicles",
        verbose_name="Brend",
    )
    car_model = models.ForeignKey(
        CarModel,
        on_delete=models.PROTECT,
        related_name="vehicles",
        verbose_name="Model",
    )

    plate_number = models.CharField(max_length=32, verbose_name="Davlat raqami")
    color = models.CharField(max_length=64, null=True, blank=True, verbose_name="Rangi")
    year = models.PositiveIntegerField(null=True, blank=True, verbose_name="Ishlab chiqarilgan yili")

    class Meta:
        verbose_name = "Avtomobil"
        verbose_name_plural = "Avtomobillar"
        constraints = [
            models.UniqueConstraint(fields=["owner", "plate_number"], name="uniq_owner_plate")
        ]

    def __str__(self):
        return f"{self.plate_number} | {self.brand} {self.car_model.name}"