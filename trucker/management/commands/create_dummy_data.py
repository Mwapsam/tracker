import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, datetime
from django.contrib.auth.models import User
from faker import Faker

from trucker.models import (
    Carrier,
    Driver,
    Vehicle,
    LogEntry,
    DutyStatus,
    CycleCalculation,
)

fake = Faker()

KNOWN_LOCATIONS = [
    {"lat": 34.052235, "lon": -118.243683, "name": "Los Angeles, CA"},
    {"lat": 36.169941, "lon": -115.139832, "name": "Las Vegas, NV"},
    {"lat": 40.712776, "lon": -74.005974, "name": "New York, NY"},
    {"lat": 41.878113, "lon": -87.629799, "name": "Chicago, IL"},
    {"lat": 29.760427, "lon": -95.369804, "name": "Houston, TX"},
    {"lat": 33.448376, "lon": -112.074036, "name": "Phoenix, AZ"},
    {"lat": 39.739236, "lon": -104.990251, "name": "Denver, CO"},
    {"lat": 47.606209, "lon": -122.332069, "name": "Seattle, WA"},
    {"lat": 25.761681, "lon": -80.191788, "name": "Miami, FL"},
    {"lat": 32.776665, "lon": -96.796989, "name": "Dallas, TX"},
    {"lat": 37.774929, "lon": -122.419418, "name": "San Francisco, CA"},
    {"lat": 33.749099, "lon": -84.390185, "name": "Atlanta, GA"},
    {"lat": 42.360082, "lon": -71.058880, "name": "Boston, MA"},
    {"lat": 39.952583, "lon": -75.165222, "name": "Philadelphia, PA"},
    {"lat": 35.227085, "lon": -80.843124, "name": "Charlotte, NC"},
    {"lat": 28.538336, "lon": -81.379234, "name": "Orlando, FL"},
    {"lat": 42.331427, "lon": -83.045753, "name": "Detroit, MI"},
    {"lat": 38.627003, "lon": -90.199402, "name": "St. Louis, MO"},
    {"lat": 44.977753, "lon": -93.265015, "name": "Minneapolis, MN"},
    {"lat": 36.162664, "lon": -86.781602, "name": "Nashville, TN"},
    {"lat": 39.099724, "lon": -94.578331, "name": "Kansas City, MO"},
    {"lat": 29.951065, "lon": -90.071533, "name": "New Orleans, LA"},
    {"lat": 45.505106, "lon": -122.675026, "name": "Portland, OR"},
    {"lat": 31.761878, "lon": -106.485022, "name": "El Paso, TX"},
    {"lat": 35.467560, "lon": -97.516428, "name": "Oklahoma City, OK"},
]

HOS_RULES = {
    "max_driving_day": 11, 
    "max_duty_day": 14,  
    "cycle_days_70": 8,  
    "cycle_days_60": 7,  
}


def day_bounds(dt: datetime):
    """Return start-of-day and end-of-day for dt."""
    start = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    return start, end


class Command(BaseCommand):
    help = "Creates HOS-compliant(ish) dummy data with realistic driver movements."

    def handle(self, *args, **options):
        carrier_name = fake.company()
        mc_number = "MC" + "".join(str(random.randint(0, 9)) for _ in range(6))
        hos_cycle_choice = random.choice(["60", "70"])

        carrier, _ = Carrier.objects.get_or_create(
            mc_number=mc_number,
            defaults={
                "name": carrier_name,
                "main_office_address": fake.address(),
                "home_terminal_address": fake.address(),
                "hos_cycle_choice": hos_cycle_choice,
            },
        )

        for i in range(1, 11):
            username = fake.user_name() + str(i)
            first_name = fake.first_name()
            last_name = fake.last_name()

            user, _ = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": fake.email(),
                },
            )
            user.set_password("password123")
            user.save()

            driver, _ = Driver.objects.get_or_create(
                user=user,
                defaults={
                    "license_number": "DL"
                    + "".join(str(random.randint(0, 9)) for _ in range(6)),
                    "carrier": carrier,
                    "current_cycle_used": 0,
                    "last_34hr_restart": timezone.now() - timedelta(days=1),
                },
            )

            vin = fake.bothify(
                "1????????????????", letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            )
            truck_number = "TRUCK" + "".join(
                str(random.randint(0, 9)) for _ in range(3)
            )
            trailer_number = "TRAILER" + "".join(
                str(random.randint(0, 9)) for _ in range(3)
            )

            vehicle, _ = Vehicle.objects.get_or_create(
                vin=vin,
                defaults={
                    "carrier": carrier,
                    "truck_number": truck_number,
                    "trailer_number": trailer_number,
                },
            )

            self.generate_logs_for_driver(driver, vehicle, days=7)

            CycleCalculation.objects.get_or_create(
                driver=driver,
                calculation_date=timezone.now().date(),
                defaults={
                    "total_hours": random.uniform(0, 70),
                    "cycle_type": f"{hos_cycle_choice}-hour",
                },
            )

        self.stdout.write(self.style.SUCCESS("Created HOS-compliant(ish) dummy data!"))

    def generate_logs_for_driver(self, driver: Driver, vehicle: Vehicle, days=7):
        """
        Generate a set of LogEntries and DutyStatus objects that attempt to follow
        basic HOS constraints: max 11 hours driving, max 14 hours on-duty per day,
        plus 10-hour breaks between 'shifts'.
        """
        current_time = timezone.now() - timedelta(days=days)
        current_odometer = random.uniform(1000, 5000)

        daily_logs = {}

        while current_time < timezone.now():
            day_start, day_end = day_bounds(current_time)
            if current_time >= day_end:
                current_time = day_end
                continue

            date_key = current_time.date()
            if date_key not in daily_logs:
                daily_logs[date_key] = LogEntry.objects.create(
                    driver=driver,
                    vehicle=vehicle,
                    date=date_key,
                    start_odometer=current_odometer,
                    end_odometer=current_odometer,
                    remarks=fake.sentence(),
                    signature=f"{driver.user.first_name} {driver.user.last_name}",
                    adverse_conditions=random.choice([True, False]),
                )

            log_entry = daily_logs[date_key]

            day_driving_hours, day_duty_hours = self.get_daily_totals(log_entry)

            if (
                day_driving_hours >= HOS_RULES["max_driving_day"]
                or day_duty_hours >= HOS_RULES["max_duty_day"]
            ):
                status_hours = random.uniform(10, 12)
                self.create_status(
                    log_entry,
                    "OFF",
                    current_time,
                    current_time + timedelta(hours=status_hours),
                )
                current_time += timedelta(hours=status_hours)
                continue

            status_type = self.pick_next_status(day_driving_hours, day_duty_hours)

            max_hours_for_status = self.get_max_status_hours(
                status_type, day_driving_hours, day_duty_hours
            )
            status_hours = random.uniform(1, max_hours_for_status)

            start_time = current_time
            end_time = current_time + timedelta(hours=status_hours)
            location = random.choice(KNOWN_LOCATIONS)
            self.create_status(log_entry, status_type, start_time, end_time, location)

            if status_type == "D":
                mph = 50  
                miles = status_hours * mph
                current_odometer += miles
                log_entry.end_odometer = current_odometer
                log_entry.save()

            current_time = end_time

    def pick_next_status(self, day_driving_hours, day_duty_hours):
        """
        Decide next status in a naive way:
         - If driving is under 8 hours, we might choose to drive again.
         - If we've driven ~8 hours, maybe pick ON or OFF.
         - Otherwise random among ON/OFF/SB.
        """
        if day_driving_hours < 8 and day_duty_hours < 12:
            return random.choice(["D", "ON", "OFF", "SB"])
        else:
            return random.choice(["ON", "OFF", "SB"])

    def get_max_status_hours(self, status_type, day_driving, day_duty):
        """
        Return how many hours we can legally spend in this status
        before hitting daily limits.
        """
        remaining_drive = HOS_RULES["max_driving_day"] - day_driving
        remaining_duty = HOS_RULES["max_duty_day"] - day_duty

        if status_type == "D":
            return max(
                1, min(4, remaining_drive)
            )  
        elif status_type == "ON":
            return max(1, min(4, remaining_duty)) 
        else:
            return max(1, 10)

    def create_status(
        self, log_entry, status_type, start_time, end_time, location=None
    ):
        """Helper to create a DutyStatus record."""
        if not location:
            location = random.choice(KNOWN_LOCATIONS)

        DutyStatus.objects.create(
            log_entry=log_entry,
            status=status_type,
            start_time=start_time,
            end_time=end_time,
            location_lat=location["lat"],
            location_lon=location["lon"],
            location_name=location["name"],
        )

    def get_daily_totals(self, log_entry):
        """
        Calculate how many hours of driving and on-duty
        have been recorded for this log entry's day so far.
        """
        duty_statuses = log_entry.duty_statuses.all()
        driving_hours = 0.0
        duty_hours = 0.0

        for ds in duty_statuses:
            duration = (ds.end_time - ds.start_time).total_seconds() / 3600
            if ds.status == "D":
                driving_hours += duration
                duty_hours += duration
            elif ds.status == "ON":
                duty_hours += duration

        return driving_hours, duty_hours
