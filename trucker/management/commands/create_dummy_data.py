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
                duty_status, created = DutyStatus.objects.get_or_create(
                    log_entry=log_entry,
                    start_time=duty_start,
                    end_time=duty_end,
                    defaults={
                        "status": status_choice,
                        "location_lat": float(fake.latitude()),
                        "location_lon": float(fake.longitude()),
                        "location_name": fake.city(),
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
