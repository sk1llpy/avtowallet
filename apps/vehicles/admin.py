# apps/vehicles/admin.py
from django.contrib import admin
from unfold.contrib.inlines.admin import TabularInline

from apps.general.admin_mixins import BaseModelAdmin
from apps.vehicles.models import Brand, CarModel, Vehicle


class CarModelInline(TabularInline):
    model = CarModel
    extra = 0
    show_change_link = True
    can_delete = True

    fields = ("name", "is_active", "created_at")
    readonly_fields = ("created_at",)

    verbose_name = "Model"
    verbose_name_plural = "Modellar"


@admin.register(Brand)
class BrandAdmin(BaseModelAdmin):
    show_delete_button = True

    list_display = ("id", "name", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "uuid")
    ordering = ("name",)
    inlines = [CarModelInline]

    fieldsets = (
        ("Brend ma’lumoti", {"fields": ("name",)}),
        ("Holat", {"fields": ("is_active",)}),
        ("Tizim", {"fields": ("uuid", "created_at", "updated_at")}),
    )


@admin.register(CarModel)
class CarModelAdmin(BaseModelAdmin):
    show_delete_button = True

    list_display = ("id", "brand", "name", "is_active", "created_at")
    list_filter = ("brand", "is_active", "created_at")
    search_fields = ("brand__name", "name", "uuid")
    ordering = ("brand__name", "name")
    autocomplete_fields = ("brand",)

    fieldsets = (
        ("Model ma’lumoti", {"fields": ("brand", "name")}),
        ("Holat", {"fields": ("is_active",)}),
        ("Tizim", {"fields": ("uuid", "created_at", "updated_at")}),
    )


@admin.register(Vehicle)
class VehicleAdmin(BaseModelAdmin):
    show_delete_button = True

    list_display = ("id", "plate_number", "owner", "brand", "car_model", "year", "color", "is_active", "created_at")
    list_filter = ("brand", "car_model", "is_active", "created_at")
    search_fields = ("plate_number", "owner__tg_id", "owner__phone_number", "brand__name", "car_model__name", "uuid")
    autocomplete_fields = ("owner", "brand", "car_model")

    fieldsets = (
        ("Ega", {"fields": ("owner",)}),
        ("Avtomobil ma’lumotlari", {"fields": ("brand", "car_model", "plate_number", "year", "color")}),
        ("Holat", {"fields": ("is_active",)}),
        ("Tizim", {"fields": ("uuid", "created_at", "updated_at")}),
    )