from math import isclose
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

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
