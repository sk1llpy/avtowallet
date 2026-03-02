# apps/payroll/admin.py
from django.contrib import admin
from apps.general.admin_mixins import BaseModelAdmin
from apps.payroll.models import SalaryProfile, WorkRecord, PayrollMonth


@admin.register(SalaryProfile)
class SalaryProfileAdmin(BaseModelAdmin):
    show_delete_button = True

    list_display = ("id", "employee", "fixed_salary", "kpi_percent", "is_active", "created_at")
    list_filter = ("kpi_percent", "is_active", "created_at")
    search_fields = ("employee__user__tg_id", "employee__user__phone_number", "uuid")
    autocomplete_fields = ("employee",)

    fieldsets = (
        ("Ishchi", {"fields": ("employee",)}),
        ("Maosh sozlamalari", {"fields": ("fixed_salary", "kpi_percent")}),
        ("Holat", {"fields": ("is_active",)}),
        ("Tizim", {"fields": ("uuid", "created_at", "updated_at")}),
    )


@admin.register(WorkRecord)
class WorkRecordAdmin(BaseModelAdmin):
    show_delete_button = True

    list_display = ("id", "employee", "booking", "amount", "kpi_percent", "kpi_amount", "performed_at", "created_at")
    list_filter = ("kpi_percent", "performed_at", "created_at")
    search_fields = ("employee__user__tg_id", "employee__user__phone_number", "booking__uuid", "uuid")
    autocomplete_fields = ("employee", "booking")

    fieldsets = (
        ("Bog‘lanish", {"fields": ("employee", "booking")}),
        ("Hisob-kitob", {"fields": ("amount", "kpi_percent", "kpi_amount")}),
        ("Vaqt", {"fields": ("performed_at",)}),
        ("Tizim", {"fields": ("uuid", "created_at", "updated_at")}),
    )


@admin.register(PayrollMonth)
class PayrollMonthAdmin(BaseModelAdmin):
    show_delete_button = True

    list_display = (
        "id",
        "employee",
        "year",
        "month",
        "fixed_salary_snapshot",
        "works_total",
        "kpi_total",
        "total_salary",
        "created_at",
    )
    list_filter = ("year", "month", "created_at")
    search_fields = ("employee__user__tg_id", "employee__user__phone_number", "uuid")
    autocomplete_fields = ("employee",)
    ordering = ("-year", "-month")

    actions = ("action_recalc",)

    fieldsets = (
        ("Davr", {"fields": ("employee", "year", "month")}),
        ("Natijalar", {"fields": ("fixed_salary_snapshot", "works_total", "kpi_total", "total_salary")}),
        ("Tizim", {"fields": ("uuid", "created_at", "updated_at")}),
    )

    @admin.action(description="Tanlangan oyliklarni qayta hisoblash")
    def action_recalc(self, request, queryset):
        for pm in queryset:
            pm.recalc()