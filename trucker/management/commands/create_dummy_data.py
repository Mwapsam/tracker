from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from trucker.models import (
    Carrier,
    Driver,
    Vehicle,
    LogEntry,
    DutyStatus,
    CycleCalculation,
)


class Command(BaseCommand):
    help = "Creates dummy data for testing purposes."

    def handle(self, *args, **options):
        # Create or get a Carrier
        carrier, created = Carrier.objects.get_or_create(
            mc_number="MC123456",
            defaults={
                "name": "Dummy Carrier",
                "main_office_address": "123 Main St",
                "home_terminal_address": "456 Terminal Rd",
                "hos_cycle_choice": "70",
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Created Carrier"))
        else:
            self.stdout.write("Carrier already exists.")

        # Create or get a User
        user, created = User.objects.get_or_create(
            username="dummyuser",
            defaults={
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
            },
        )
        if created:
            user.set_password("password123")
            user.save()
            self.stdout.write(self.style.SUCCESS("Created User"))
        else:
            self.stdout.write("User already exists.")

        # Create or get a Driver linked to the User and Carrier
        driver, created = Driver.objects.get_or_create(
            user=user,
            defaults={
                "license_number": "DL987654",
                "carrier": carrier,
                "current_cycle_used": 0,
                "last_34hr_restart": timezone.now() - timedelta(days=2),
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Created Driver"))
        else:
            self.stdout.write("Driver already exists.")

        # Create or get a Vehicle
        vehicle, created = Vehicle.objects.get_or_create(
            vin="1HGBH41JXMN109186",
            defaults={
                "carrier": carrier,
                "truck_number": "TRUCK001",
                "trailer_number": "TRAILER001",
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Created Vehicle"))
        else:
            self.stdout.write("Vehicle already exists.")

        # Create or get a LogEntry
        now = timezone.now()
        log_entry, created = LogEntry.objects.get_or_create(
            driver=driver,
            vehicle=vehicle,
            date=now.date(),
            defaults={
                "start_odometer": 1000.0,
                "end_odometer": 1200.0,
                "remarks": "Dummy log entry for testing",
                "signature": "John Doe",
                "adverse_conditions": False,
                "duty_window_start": now,
                "duty_window_end": now
                + timedelta(hours=13),  # Valid within the 14-hour limit
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Created LogEntry"))
        else:
            self.stdout.write("LogEntry already exists.")

        # Create or get a DutyStatus for the LogEntry
        duty_status, created = DutyStatus.objects.get_or_create(
            log_entry=log_entry,
            start_time=now,
            end_time=now + timedelta(hours=2),
            defaults={
                "status": "D",
                "location_lat": 34.0522,
                "location_lon": -118.2437,
                "location_name": "Los Angeles, CA",
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Created DutyStatus"))
        else:
            self.stdout.write("DutyStatus already exists.")

        # Create or get a CycleCalculation record
        calc, created = CycleCalculation.objects.get_or_create(
            driver=driver,
            calculation_date=now.date(),
            defaults={"total_hours": 50.0, "cycle_type": "70-hour"},
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Created CycleCalculation"))
        else:
            self.stdout.write("CycleCalculation already exists.")

        self.stdout.write(self.style.SUCCESS("Dummy data creation complete."))
