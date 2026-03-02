# apps/bookings/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.bookings.models import BookingService


@receiver(post_save, sender=BookingService)
def bookingservice_saved(sender, instance: BookingService, **kwargs):
    instance.booking.recalc_total()


@receiver(post_delete, sender=BookingService)
def bookingservice_deleted(sender, instance: BookingService, **kwargs):
    instance.booking.recalc_total()