# apps/general/admin_mixins.py
from unfold.admin import ModelAdmin


class BaseModelAdmin(ModelAdmin):
    """
    Unfold uchun umumiy admin sozlamalar:
    - Delete button ko‘rsatish
    - created_at/updated_at/uuid readonly
    """
    show_delete_button = True

    readonly_fields = ("uuid", "created_at", "updated_at")
    ordering = ("-created_at",)
    list_per_page = 50