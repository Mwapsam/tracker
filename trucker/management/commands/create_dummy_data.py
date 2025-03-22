import random
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
from faker import Faker

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


class Command(BaseCommand):
    help = "Creates dynamic dummy data for testing purposes with at least 10 drivers and their logs."

    def handle(self, *args, **options):
        carrier_name = fake.company()
        mc_number = "MC" + "".join(str(random.randint(0, 9)) for _ in range(6))
        main_office_address = fake.address()
        home_terminal_address = fake.address()
        hos_cycle_choice = random.choice(["60", "70"])

        carrier, created = Carrier.objects.get_or_create(
            mc_number=mc_number,
            defaults={
                "name": carrier_name,
                "main_office_address": main_office_address,
                "home_terminal_address": home_terminal_address,
                "hos_cycle_choice": hos_cycle_choice,
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created Carrier: {carrier_name}"))
        else:
            self.stdout.write("Carrier already exists.")

        for driver_index in range(1, 11):
            username = fake.user_name() + str(driver_index)
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = fake.email()

            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                },
            )
            if created:
                user.set_password("password123")
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Created User: {username}"))
            else:
                self.stdout.write(f"User {username} already exists.")

            license_number = "DL" + "".join(str(random.randint(0, 9)) for _ in range(6))
            driver, created = Driver.objects.get_or_create(
                user=user,
                defaults={
                    "license_number": license_number,
                    "carrier": carrier,
                    "current_cycle_used": round(
                        (
                            random.uniform(0, 70)
                            if hos_cycle_choice == "70"
                            else random.uniform(0, 60)
                        ),
                        2,
                    ),
                    "last_34hr_restart": timezone.now()
                    - timedelta(days=random.randint(1, 3)),
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created Driver {driver_index}"))
            else:
                self.stdout.write(f"Driver {driver_index} already exists.")

            vin = fake.bothify(
                text="1????????????????", letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            )
            truck_number = "TRUCK" + "".join(
                str(random.randint(0, 9)) for _ in range(3)
            )
            trailer_number = "TRAILER" + "".join(
                str(random.randint(0, 9)) for _ in range(3)
            )
            vehicle, created = Vehicle.objects.get_or_create(
                vin=vin,
                defaults={
                    "carrier": carrier,
                    "truck_number": truck_number,
                    "trailer_number": trailer_number,
                },
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Created Vehicle for Driver {driver_index}")
                )
            else:
                self.stdout.write(f"Vehicle for Driver {driver_index} already exists.")

            for log_index in range(1, 11):
                now_time = timezone.now() + timedelta(minutes=log_index)
                start_odometer = round(random.uniform(1000, 5000), 2)
                end_odometer = start_odometer + round(random.uniform(50, 500), 2)
                log_entry, created = LogEntry.objects.get_or_create(
                    driver=driver,
                    vehicle=vehicle,
                    date=now_time.date(),
                    defaults={
                        "start_odometer": start_odometer,
                        "end_odometer": end_odometer,
                        "remarks": fake.sentence(nb_words=6),
                        "signature": f"{first_name} {last_name}",
                        "adverse_conditions": random.choice([True, False]),
                    },
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Created LogEntry {log_index} for Driver {driver_index}"
                        )
                    )
                else:
                    self.stdout.write(
                        f"LogEntry {log_index} for Driver {driver_index} already exists."
                    )

                duty_start = now_time
                duty_end = duty_start + timedelta(hours=random.randint(1, 4))
                status_choice = random.choice(["D", "ON", "OFF", "SB"])

                # 1) Pick a random location from KNOWN_LOCATIONS
                chosen_location = random.choice(KNOWN_LOCATIONS)
                lat = chosen_location["lat"]
                lon = chosen_location["lon"]
                location_name = chosen_location["name"]

                duty_status, created = DutyStatus.objects.get_or_create(
                    log_entry=log_entry,
                    start_time=duty_start,
                    end_time=duty_end,
                    defaults={
                        "status": status_choice,
                        # 2) Use real coordinates and name
                        "location_lat": lat,
                        "location_lon": lon,
                        "location_name": location_name,
                    },
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Created DutyStatus for LogEntry {log_index} of Driver {driver_index}"
                        )
                    )
                else:
                    self.stdout.write(
                        f"DutyStatus for LogEntry {log_index} of Driver {driver_index} already exists."
                    )

            total_hours = round(random.uniform(0, 70), 2)
            cycle_calculation, created = CycleCalculation.objects.get_or_create(
                driver=driver,
                calculation_date=timezone.now().date(),
                defaults={
                    "total_hours": total_hours,
                    "cycle_type": f"{hos_cycle_choice}-hour",
                },
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created CycleCalculation for Driver {driver_index}"
                    )
                )
            else:
                self.stdout.write(
                    f"CycleCalculation for Driver {driver_index} already exists."
                )

        self.stdout.write(self.style.SUCCESS("Dynamic dummy data creation complete."))
