# apps/services/admin.py
from django.contrib import admin
from apps.general.admin_mixins import BaseModelAdmin
from apps.services.models import ServiceCategory, Service, ServiceScope


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(BaseModelAdmin):
    show_delete_button = True

    list_display = ("id", "title", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("title", "uuid")
    ordering = ("title",)

    fieldsets = (
        ("Kategoriya", {"fields": ("title",)}),
        ("Holat", {"fields": ("is_active",)}),
        ("Tizim", {"fields": ("uuid", "created_at", "updated_at")}),
    )


@admin.register(Service)
class ServiceAdmin(BaseModelAdmin):
    show_delete_button = True

    list_display = ("id", "title", "category", "price", "scope", "duration_minutes", "is_active", "created_at")
    list_filter = ("scope", "category", "is_active", "created_at")
    search_fields = ("title", "category__title", "uuid")
    ordering = ("title",)
    autocomplete_fields = ("category", "allowed_brands", "allowed_models")

    fieldsets = (
        ("Asosiy ma’lumot", {"fields": ("title", "category", "price", "duration_minutes")}),
        ("Qamrov (MTM)", {"fields": ("scope", "allowed_brands", "allowed_models")}),
        ("Holat", {"fields": ("is_active",)}),
        ("Tizim", {"fields": ("uuid", "created_at", "updated_at")}),
    )

    @admin.display(description="MTM rejimi?")
    def mtm_mode(self, obj: Service):
        return "Ha" if obj.scope == ServiceScope.LIMITED else "Yo‘q"