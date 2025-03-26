from django.db.models.signals import post_save
from django.dispatch import receiver
from trucker.models import Trip


@receiver(post_save, sender=Trip)
def generate_trip_stops(sender, instance, created, **kwargs):
    if created:
        instance.generate_stops()
