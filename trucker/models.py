from datetime import timedelta, datetime
from django.db import models, transaction
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.utils.timezone import is_aware, make_aware, get_current_timezone
from django.dispatch import receiver
from django.conf import settings

from model_utils import FieldTracker

from trucker.services.route_services import calculate_route_distance
from trucker.services.stop_services import calculate_fuel_stops, calculate_rest_stops
from trucker.validators import (
    check_34_hour_restart,
    validate_11_hour_driving_limit,
    validate_14_hour_duty_window,
    validate_30_minute_break,
    validate_overlapping_statuses,
)


class Carrier(models.Model):
    name = models.CharField(max_length=100)
    mc_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    main_office_address = models.TextField(null=True, blank=True)
    home_terminal_address = models.TextField(null=True, blank=True)
    hos_cycle_choice = models.CharField(
        max_length=2,
        choices=[("60", "60-hour/7-day"), ("70", "70-hour/8-day")],
        default="70",
    )

    def __str__(self):
        return f"{self.name} (MC#{self.mc_number})"


class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    license_number = models.CharField(max_length=50)
    carrier = models.ForeignKey(
        Carrier, on_delete=models.CASCADE, null=True, blank=True
    )
    current_cycle_used = models.FloatField(default=0)
    last_34hr_restart = models.DateTimeField(null=True, blank=True)

    def remaining_hours(self):
        if not self.carrier:
            return 0
        cycle_hours = 70 if self.carrier.hos_cycle_choice == "70" else 60
        return max(cycle_hours - self.current_cycle_used, 0)

    def check_34hr_restart(self, restart_time):
        thirty_four_hours_ago = restart_time - timezone.timedelta(hours=34)
        overlapping_statuses = DutyStatus.objects.filter(
            log_entry__driver=self,
            start_time__lt=restart_time,
            end_time__gt=thirty_four_hours_ago,
        ).exclude(status__in=["OFF", "SB"])

        if not overlapping_statuses.exists():
            self.last_34hr_restart = restart_time
            self.save()
            return True
        return False

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.license_number})"


class Trip(models.Model):
    driver = models.ForeignKey("Driver", on_delete=models.CASCADE)
    vehicle = models.ForeignKey(
        "Vehicle",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    current_location = models.CharField(max_length=200)
    pickup_location = models.CharField(max_length=200)
    dropoff_location = models.CharField(max_length=200)
    distance = models.FloatField(null=True, blank=True)
    estimated_duration = models.DurationField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    start_time = models.DateTimeField(default=timezone.now)
    average_speed = models.FloatField(default=50)
    completed_at = models.DateTimeField(null=True, blank=True)
    completed = models.BooleanField(default=False)

    tracker = FieldTracker(
        fields=["distance", "pickup_location", "dropoff_location", "start_time"]
    )

    def __str__(self):
        return self.driver.user.username

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["driver"],
                condition=models.Q(completed=False),
                name="unique_active_trip_per_driver",
            )
        ]

    def save(self, *args, **kwargs):
        if self.pk is None and not self.completed:
            if Trip.objects.filter(driver=self.driver, completed=False).exists():
                raise ValidationError("Driver already has an active trip")

        if not self.distance or not self.estimated_duration:
            self.calculate_route_details()

        super().save(*args, **kwargs)

    def calculate_route_details(self):
        try:
            distance, duration = calculate_route_distance(
                self.pickup_location, self.dropoff_location
            )

            self.distance = distance
            self.estimated_duration = timedelta(hours=duration)

        except Exception as e:
            raise ValidationError(f"Route calculation failed: {str(e)}") from e

    def generate_stops(self):
        with transaction.atomic():
            self.stops.all().delete()

            try:
                fuel_stops = calculate_fuel_stops(
                    self.distance,
                    self.start_time,
                    origin=self.pickup_location,
                    destination=self.dropoff_location,
                    api_key=settings.MAPS_API_KEY,
                )
                validated_fuel = [
                    self.validate_stop_data(stop, "FUEL") for stop in fuel_stops
                ]
                Stop.objects.bulk_create(
                    [Stop(trip=self, **stop) for stop in validated_fuel]
                )

                rest_stops = calculate_rest_stops(
                    total_miles=self.distance,
                    start_time=self.start_time,
                    origin=self.pickup_location,
                    destination=self.dropoff_location,
                    api_key=settings.MAPS_API_KEY,
                )
                validated_rest = [
                    self.validate_stop_data(stop, "REST") for stop in rest_stops
                ]
                Stop.objects.bulk_create(
                    [Stop(trip=self, **stop) for stop in validated_rest]
                )

            except Exception as e:
                raise ValidationError(f"Stop generation failed: {str(e)}") from e

    def validate_stop_data(self, stop_data: dict, expected_type: str) -> dict:
        required_fields = {
            "location_name": str,
            "location_lat": float,
            "location_lon": float,
            "scheduled_time": (datetime, timezone.datetime),
            "duration": (timedelta, timezone.timedelta),
        }

        if stop_data.get("stop_type", "") != expected_type:
            raise ValidationError(
                f"Invalid stop_type: {stop_data.get('stop_type')}. Expected {expected_type}"
            )

        for field, field_type in required_fields.items():
            if field not in stop_data:
                raise ValidationError(f"Missing required field: {field}")

            if not isinstance(stop_data[field], field_type):
                raise ValidationError(
                    f"Invalid type for {field}. Expected {field_type}, got {type(stop_data[field])}"
                )

        if isinstance(stop_data["scheduled_time"], datetime):
            stop_data["scheduled_time"] = timezone.make_aware(
                stop_data["scheduled_time"]
            )

        if not (-90 <= stop_data["location_lat"] <= 90):
            raise ValidationError(f"Invalid latitude: {stop_data['location_lat']}")

        if not (-180 <= stop_data["location_lon"] <= 180):
            raise ValidationError(f"Invalid longitude: {stop_data['location_lon']}")

        return stop_data


class Stop(models.Model):
    class StopType(models.TextChoices):
        FUEL = "FUEL", "Fuel Stop"
        REST = "REST", "Rest Break"
        LOAD = "LOAD", "Loading/Unloading"

    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="stops")
    stop_type = models.CharField(max_length=10, choices=StopType.choices)
    location_name = models.CharField(max_length=255)
    location_lat = models.FloatField(null=True, blank=True)
    location_lon = models.FloatField(null=True, blank=True)
    scheduled_time = models.DateTimeField()
    actual_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(default=timezone.timedelta(minutes=30))

    def __str__(self):
        return f"{self.get_stop_type_display()} at {self.location_name}"

    class Meta:
        ordering = ["scheduled_time"]
        indexes = [
            models.Index(fields=["scheduled_time", "stop_type"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(location_lat__gte=-90) & models.Q(location_lat__lte=90),
                name="valid_latitude",
            ),
            models.CheckConstraint(
                check=models.Q(location_lon__gte=-180)
                & models.Q(location_lon__lte=180),
                name="valid_longitude",
            ),
        ]

    def clean(self):
        if self.scheduled_time < timezone.now():
            raise ValidationError("Scheduled time cannot be in the past")

        if self.duration.total_seconds() < 1800:
            raise ValidationError("Minimum stop duration is 30 minutes")


class Vehicle(models.Model):
    carrier = models.ForeignKey(
        Carrier, on_delete=models.CASCADE, null=True, blank=True
    )
    truck_number = models.CharField(max_length=20)
    trailer_number = models.CharField(max_length=20, blank=True)
    vin = models.CharField(max_length=17, unique=True, null=True, blank=True)

    def __str__(self):
        return f"{self.truck_number} - {self.trailer_number or 'No Trailer'}"


class LogEntry(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name="logs")
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    start_odometer = models.FloatField()
    end_odometer = models.FloatField()
    total_miles = models.FloatField(editable=False, null=True, blank=True)
    remarks = models.TextField(blank=True)
    signature = models.CharField(max_length=100)
    adverse_conditions = models.BooleanField(default=False)

    def clean(self):
        if self.end_odometer < self.start_odometer:
            raise ValidationError(
                "End odometer reading cannot be lower than start odometer."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        self.total_miles = self.end_odometer - self.start_odometer
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.driver} - {self.date}"

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_odometer__gte=models.F("start_odometer")),
                name="end_odometer_gte_start",
            )
        ]


class DutyStatus(models.Model):
    STATUS_CHOICES = [
        ("OFF", "Off Duty"),
        ("SB", "Sleeper Berth"),
        ("D", "Driving"),
        ("ON", "On Duty (Not Driving)"),
    ]

    log_entry = models.ForeignKey(
        "LogEntry", on_delete=models.CASCADE, related_name="duty_statuses"
    )
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, default="OFF")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location_lat = models.FloatField(null=True, blank=True)
    location_lon = models.FloatField(null=True, blank=True)
    location_name = models.CharField(max_length=100)

    @property
    def duration(self):
        return (self.end_time - self.start_time).total_seconds() / 3600

    def clean(self):
        if self.status in ["Pickup", "Dropoff"]:
            if (self.end_time - self.start_time).seconds != 3600:
                raise ValidationError(f"{self.status} must be exactly 1 hour long.")

        if self.status == "SB":
            min_duration = 6 * 3600
            if (self.end_time - self.start_time).total_seconds() < min_duration:
                raise ValidationError("Sleeper berth must be at least 6 hours long.")

        statuses = list(self.__class__.objects.filter(log_entry=self.log_entry))
        if self.pk:
            statuses = [s for s in statuses if s.pk != self.pk]
        statuses.append(self)
        statuses.sort(key=lambda s: s.start_time)

        validate_overlapping_statuses(statuses, self)
        if self.status in ["D", "ON"]:
            validate_14_hour_duty_window(statuses, self.log_entry.adverse_conditions)
        if self.status == "D":
            validate_11_hour_driving_limit(statuses)
            validate_30_minute_break(statuses)
        if self.status in ["OFF", "SB"]:
            check_34_hour_restart(self)

    def get_status_display(self):
        mapping = dict(self.STATUS_CHOICES)
        return mapping.get(self.status, self.status)

    def __str__(self):
        return f"{self.get_status_display()} ({self.start_time} - {self.end_time})"

    class Meta:
        ordering = ["start_time"]
        indexes = [models.Index(fields=["log_entry", "start_time"])]


@receiver([post_save, post_delete], sender=DutyStatus)
def update_driver_cycle(sender, instance, **kwargs):
    driver = instance.log_entry.driver
    cycle_days = 8 if driver.carrier.hos_cycle_choice == "70" else 7
    end_date = timezone.now().date()
    start_date = end_date - timezone.timedelta(days=cycle_days)

    statuses = DutyStatus.objects.filter(
        log_entry__driver=driver,
        status__in=["D", "ON"],
        start_time__gte=start_date,
    )
    if driver.last_34hr_restart:
        statuses = statuses.filter(start_time__gte=driver.last_34hr_restart)

    driver.current_cycle_used = sum(s.duration for s in statuses)
    driver.save()


class CycleCalculation(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    calculation_date = models.DateField()
    total_hours = models.FloatField()
    cycle_type = models.CharField(max_length=10)

    class Meta:
        unique_together = ("driver", "calculation_date")
