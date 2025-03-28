from django.db.models.signals import post_save
from django.dispatch import receiver
from trucker.models import Trip


@receiver(post_save, sender=Trip)
def update_trip_stops(sender, instance, created, **kwargs):
    critical_fields = ["distance", "pickup_location", "dropoff_location", "start_time"]
    if created or any(instance.tracker.has_changed(field) for field in critical_fields):
        instance.generate_stops()
