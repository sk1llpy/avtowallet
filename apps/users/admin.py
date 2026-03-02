# apps/users/admin.py
from django.contrib import admin
from apps.general.admin_mixins import BaseModelAdmin
from apps.users.models import User, Employee


@admin.register(User)
class UserAdmin(BaseModelAdmin):
    show_delete_button = True

    list_display = (
        "id",
        "tg_id",
        "tg_username",
        "tg_full_name",
        "first_name",
        "last_name",
        "phone_number",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "created_at")
    search_fields = (
        "tg_id",
        "tg_username",
        "tg_full_name",
        "first_name",
        "last_name",
        "phone_number",
        "uuid",
    )

    fieldsets = (
        ("Telegram ma’lumotlari", {"fields": ("tg_id", "tg_username", "tg_full_name")}),
        ("Kontakt", {"fields": ("phone_number",)}),
        ("Shaxsiy ma’lumotlar", {"fields": ("first_name", "last_name")}),
        ("Holat", {"fields": ("is_active",)}),
        ("Tizim", {"fields": ("uuid", "created_at", "updated_at")}),
    )


@admin.register(Employee)
class EmployeeAdmin(BaseModelAdmin):
    show_delete_button = True

    list_display = ("id", "user", "position", "is_master", "is_manager", "is_active", "created_at")
    list_filter = ("is_master", "is_manager", "is_active", "created_at")
    search_fields = ("user__tg_id", "user__phone_number", "user__first_name", "user__last_name", "position", "uuid")
    autocomplete_fields = ("user",)

    fieldsets = (
        ("Bog‘lanish", {"fields": ("user",)}),
        ("Ishchi ma’lumotlari", {"fields": ("position",)}),
        ("Rollar", {"fields": ("is_master", "is_manager")}),
        ("Holat", {"fields": ("is_active",)}),
        ("Tizim", {"fields": ("uuid", "created_at", "updated_at")}),
    )