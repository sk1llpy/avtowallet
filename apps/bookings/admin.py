# apps/bookings/admin.py
from django.contrib import admin, messages
from django.shortcuts import redirect

from unfold.contrib.inlines.admin import TabularInline

from apps.general.admin_mixins import BaseModelAdmin
from apps.bookings.models import Booking, BookingService, BookingStatus


class BookingServiceInline(TabularInline):
    model = BookingService
    extra = 0
    show_change_link = True
    can_delete = True

    autocomplete_fields = ("service",)

    fields = ("service", "qty", "price", "is_active", "created_at")
    readonly_fields = ("created_at",)

    verbose_name = "Bron xizmati"
    verbose_name_plural = "Bron xizmatlari"


@admin.register(Booking)
class BookingAdmin(BaseModelAdmin):
    show_delete_button = True

    list_display = (
        "id",
        "client",
        "vehicle",
        "booking_date",
        "booking_time",
        "status",
        "employee",
        "total_amount",
        "completed_at",
        "created_at",
    )
    list_filter = ("status", "booking_date", "employee", "created_at")
    search_fields = (
        "client__tg_id",
        "client__phone_number",
        "vehicle__plate_number",
        "employee__user__tg_id",
        "uuid",
    )
    ordering = ("-booking_date", "-booking_time")

    autocomplete_fields = ("client", "vehicle", "employee")
    inlines = [BookingServiceInline]

    actions = ("action_mark_confirmed", "action_mark_in_progress", "action_complete")

    fieldsets = (
        ("Mijoz", {"fields": ("client", "vehicle")}),
        ("Bron vaqti", {"fields": ("booking_date", "booking_time")}),
        ("Jarayon", {"fields": ("status", "employee", "note")}),
        ("Yakun (hisob)", {"fields": ("total_amount", "completed_at")}),
        ("Tizim", {"fields": ("uuid", "created_at", "updated_at")}),
    )

    @admin.action(description="Status: Tasdiqlandi (CONFIRMED)")
    def action_mark_confirmed(self, request, queryset):
        updated = queryset.exclude(status__in=[BookingStatus.CANCELLED, BookingStatus.COMPLETED]) \
            .update(status=BookingStatus.CONFIRMED)
        self.message_user(request, f"✅ {updated} ta booking CONFIRMED qilindi.", level=messages.SUCCESS)

    @admin.action(description="Status: Jarayonda (IN_PROGRESS)")
    def action_mark_in_progress(self, request, queryset):
        updated = queryset.exclude(status__in=[BookingStatus.CANCELLED, BookingStatus.COMPLETED]) \
            .update(status=BookingStatus.IN_PROGRESS)
        self.message_user(request, f"✅ {updated} ta booking IN_PROGRESS qilindi.", level=messages.SUCCESS)

    @admin.action(description="Tanlangan bookinglarni yakunlash (COMPLETED)")
    def action_complete(self, request, queryset):
        # har bir booking employee bo‘lsa yakunlaymiz
        ok, fail = 0, 0
        for b in queryset.select_related("employee", "vehicle"):
            try:
                if not b.employee:
                    fail += 1
                    continue
                b.complete(employee=b.employee)
                ok += 1
            except Exception:
                fail += 1

        if ok:
            self.message_user(request, f"✅ {ok} ta booking yakunlandi.", level=messages.SUCCESS)
        if fail:
            self.message_user(
                request,
                f"⚠️ {fail} ta booking yakunlanmadi (employee yo‘q yoki xatolik).",
                level=messages.WARNING,
            )


@admin.register(BookingService)
class BookingServiceAdmin(BaseModelAdmin):
    show_delete_button = True

    list_display = ("id", "booking", "service", "qty", "price", "is_active", "created_at")
    list_filter = ("service", "is_active", "created_at")
    search_fields = ("booking__uuid", "service__title", "uuid")
    autocomplete_fields = ("booking", "service")

    fieldsets = (
        ("Bog‘lanish", {"fields": ("booking", "service")}),
        ("Hisob", {"fields": ("qty", "price")}),
        ("Holat", {"fields": ("is_active",)}),
        ("Tizim", {"fields": ("uuid", "created_at", "updated_at")}),
    )