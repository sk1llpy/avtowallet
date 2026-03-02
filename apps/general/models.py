# apps/general/models.py
from uuid import uuid4
from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan vaqti")

    uuid = models.UUIDField(
        default=uuid4,
        unique=True,
        editable=False,
        verbose_name="Unikal identifikator (UUID)",
    )

    is_active = models.BooleanField(default=True, verbose_name="Faol holatda")

    class Meta:
        abstract = True
        ordering = ("-created_at",)