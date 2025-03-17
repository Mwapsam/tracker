from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone


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
    current_cycle_used = models.FloatField(default=0)  # Track 60/70-hour limit
    last_34hr_restart = models.DateTimeField(null=True, blank=True)

    def remaining_hours(self):
        cycle_hours = 70 if self.carrier.hos_cycle_choice == "70" else 60
        return max(cycle_hours - self.current_cycle_used, 0)

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

    # Track critical HOS windows
    duty_window_start = models.DateTimeField(null=True, blank=True)
    duty_window_end = models.DateTimeField(null=True, blank=True)

    def clean(self):
        if self.duty_window_start and self.duty_window_end:
            duration = self.duty_window_end - self.duty_window_start
            if duration.total_seconds() > 14 * 3600 and not self.adverse_conditions:
                raise ValidationError(
                    "14-hour duty window exceeded without adverse conditions exception"
                )
        if self.end_odometer < self.start_odometer:
            raise ValidationError(
                "End odometer reading cannot be lower than start odometer."
            )

    def save(self, *args, **kwargs):
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
        LogEntry, on_delete=models.CASCADE, related_name="duty_statuses"
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
        # Prevent overlapping statuses
        overlaps = DutyStatus.objects.filter(
            log_entry=self.log_entry,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        ).exclude(pk=self.pk)

        if overlaps.exists():
            raise ValidationError("Duty status periods cannot overlap")

    class Meta:
        ordering = ["start_time"]
        indexes = [
            models.Index(fields=["log_entry", "start_time"]),
        ]

    def __str__(self):
        return f"{self.get_status_display()} ({self.start_time} - {self.end_time})"


class CycleCalculation(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    calculation_date = models.DateField()
    total_hours = models.FloatField()
    cycle_type = models.CharField(max_length=10)

    class Meta:
        unique_together = ("driver", "calculation_date")
