import datetime
import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone

from trips.models import Carrier, Driver, Vehicle, LogEntry, DutyStatus, CycleCalculation

class Command(BaseCommand):
    help = "Create dummy data for testing HOS models"

    def handle(self, *args, **options):
        # 1) Create a few Carriers
        carriers = [
            {
                "name": "ACME Trucking",
                "mc_number": "MC123456",
                "main_office_address": "123 Main St, Dallas, TX",
                "home_terminal_address": "Dallas Terminal",
                "hos_cycle_choice": "70",
            },
            {
                "name": "FastHaul Logistics",
                "mc_number": "MC789012",
                "main_office_address": "987 Elm St, Atlanta, GA",
                "home_terminal_address": "Atlanta Terminal",
                "hos_cycle_choice": "60",
            },
        ]
        carrier_objs = []
        for c in carriers:
            obj, created = Carrier.objects.get_or_create(
                mc_number=c["mc_number"],
                defaults=c
            )
            carrier_objs.append(obj)

        # 2) Create some Users & Drivers
        user1 = User.objects.create_user(
            username="driver_jane",
            password="password123",
            first_name="Jane",
            last_name="Doe"
        )
        user2 = User.objects.create_user(
            username="driver_john",
            password="password123",
            first_name="John",
            last_name="Smith"
        )

        driver1, _ = Driver.objects.get_or_create(
            user=user1,
            carrier=carrier_objs[0],
            license_number="TX1234567",
            defaults={"current_cycle_used": 10.0},
        )
        driver2, _ = Driver.objects.get_or_create(
            user=user2,
            carrier=carrier_objs[1],
            license_number="GA9876543",
            defaults={"current_cycle_used": 25.0},
        )

        # 3) Create Vehicles
        vehicles_data = [
            {
                "carrier": carrier_objs[0],
                "truck_number": "T100",
                "trailer_number": "TR1",
                "vin": "VIN00000000000001",
            },
            {
                "carrier": carrier_objs[0],
                "truck_number": "T200",
                "trailer_number": "",
                "vin": "VIN00000000000002",
            },
            {
                "carrier": carrier_objs[1],
                "truck_number": "T300",
                "trailer_number": "TR9",
                "vin": "VIN00000000000003",
            },
        ]
        vehicle_objs = []
        for v in vehicles_data:
            vo, _ = Vehicle.objects.get_or_create(vin=v["vin"], defaults=v)
            vehicle_objs.append(vo)

        # 4) Create LogEntries
        log_entries = []
        for i in range(3):
            for drv in [driver1, driver2]:
                vehicle_choice = random.choice(vehicle_objs)
                start_odom = random.uniform(1000, 2000)
                end_odom = start_odom + random.uniform(50, 200)

                log = LogEntry.objects.create(
                    driver=drv,
                    vehicle=vehicle_choice,
                    date=timezone.now().date() - datetime.timedelta(days=i),
                    start_odometer=start_odom,
                    end_odometer=end_odom,
                    remarks="Sample log entry",
                    signature=f"{drv.user.get_full_name()}",
                    duty_window_start=timezone.now() - datetime.timedelta(hours=14),
                    duty_window_end=timezone.now(),  # random example
                    adverse_conditions=(i == 1),  # just for demonstration
                )
                log_entries.append(log)

        # 5) Create DutyStatuses
        for log in log_entries:
            base_start = datetime.datetime.combine(log.date, datetime.time(0, 0))
            times = [
                ("D", 6),   # 6 hours driving
                ("ON", 2),  # 2 hours on-duty not driving
                ("OFF", 8), # 8 hours off
                ("SB", 8),  # 8 hours sleeper (complete 24h)
            ]
            current_start = base_start
            for (status_code, hours) in times:
                st = timezone.make_aware(current_start)
                et = st + datetime.timedelta(hours=hours)
                DutyStatus.objects.create(
                    log_entry=log,
                    status=status_code,
                    start_time=st,
                    end_time=et,
                    location_lat=32.7767 + random.random(),
                    location_lon=-96.7970 + random.random(),
                    location_name="Random Place",
                )
                current_start = et

        # 6) Create CycleCalculations
        for drv in [driver1, driver2]:
            for i in range(3):
                day = timezone.now().date() - datetime.timedelta(days=i)
                CycleCalculation.objects.update_or_create(
                    driver=drv,
                    calculation_date=day,
                    defaults={
                        "total_hours": random.uniform(0, 11),
                        "cycle_type": f"{drv.carrier.hos_cycle_choice}-hour",
                    },
                )

        self.stdout.write(self.style.SUCCESS("Dummy data created successfully!"))
