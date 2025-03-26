from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random
from faker import Faker

from trucker.models import Driver, Carrier, Vehicle, Trip, Stop, LogEntry, DutyStatus

fake = Faker()

# Real coordinates along common US trucking routes
ROUTE_COORDINATES = {
    "los_angeles": (34.052235, -118.243683),
    "san_francisco": (37.7749, -122.4194),
    "bakersfield": (35.373292, -119.018713),
    "phoenix": (33.448376, -112.074036),
    "flagstaff": (35.198284, -111.651299),
    "albuquerque": (35.084103, -106.650985),
    "amarillo": (35.221997, -101.831297),
    "oklahoma_city": (35.467560, -97.516428),
    "st_louis": (38.627003, -90.199402),
    "indianapolis": (39.768403, -86.158068),
    "columbus": (39.961176, -82.998794),
    "new_york": (40.712776, -74.005974),
}


def generate_fuel_stops(distance, start_time):
    """Generate realistic fuel stops along the route."""
    stops = []
    miles_per_stop = 500  # For testing, we use a stop every 500 miles.
    current_mile = miles_per_stop

    while current_mile < distance:
        # Pick a random city from our route coordinates except the first and last keys.
        city_key = random.choice(list(ROUTE_COORDINATES.keys())[1:-1])
        lat, lon = ROUTE_COORDINATES[city_key]

        stops.append(
            {
                "stop_type": "FUEL",
                "location_name": f"{fake.city()} Truck Stop",
                "location_lat": lat
                + random.uniform(-0.05, 0.05),  # add slight variance
                "location_lon": lon + random.uniform(-0.05, 0.05),
                "scheduled_time": start_time
                + timedelta(hours=current_mile / 55),  # assume average 55 mph
                "duration": timedelta(minutes=30),
            }
        )
        current_mile += miles_per_stop

    return stops


def generate_rest_stops(duration_hours, start_time):
    """Generate realistic rest stops along the route."""
    stops = []
    hours_between_rest = 8  # DOT requirement
    current_hour = hours_between_rest
    while current_hour < duration_hours:
        city_key = random.choice(list(ROUTE_COORDINATES.keys())[1:-1])
        lat, lon = ROUTE_COORDINATES[city_key]

        stops.append(
            {
                "stop_type": "REST",
                "location_name": f"{fake.city()} Rest Area",
                "location_lat": lat + random.uniform(-0.05, 0.05),
                "location_lon": lon + random.uniform(-0.05, 0.05),
                "scheduled_time": start_time + timedelta(hours=current_hour),
                "duration": timedelta(hours=10),  # 10 hour rest period
            }
        )
        current_hour += hours_between_rest
    return stops


class Command(BaseCommand):
    help = "Create realistic dummy data for testing the trucking application"

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            type=str,
            default="driver1",
            help="Username for the dummy driver",
        )
        parser.add_argument(
            "--carrier",
            type=str,
            default="Test Carrier",
            help="Carrier name for the driver",
        )
        parser.add_argument(
            "--trips",
            type=int,
            default=3,
            help="Number of trips to create",
        )

    def handle(self, *args, **options):
        username = options["username"]
        carrier_name = options["carrier"]
        num_trips = options["trips"]

        # Create or get the user.
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                "email": f"{username}@example.com",
                "password": "password123",
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created user {user.username}"))
        else:
            self.stdout.write(
                self.style.WARNING(f"User {user.username} already exists")
            )

        # Create or get the carrier.
        carrier, created = Carrier.objects.get_or_create(
            name=carrier_name,
            defaults={
                "mc_number": f"MC{fake.random_number(digits=6)}",
                "main_office_address": fake.address(),
                "home_terminal_address": fake.address(),
                "hos_cycle_choice": "70",
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created carrier {carrier.name}"))
        else:
            self.stdout.write(
                self.style.WARNING(f"Carrier {carrier.name} already exists")
            )

        # Create or get the driver.
        driver, created = Driver.objects.get_or_create(
            user=user,
            defaults={
                "license_number": f"DL{fake.random_number(digits=8)}",
                "carrier": carrier,
                "current_cycle_used": random.randint(0, 60),
                "last_34hr_restart": timezone.now()
                - timedelta(days=random.randint(1, 30)),
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created driver {driver}"))
        else:
            self.stdout.write(self.style.WARNING(f"Driver {driver} already exists"))

        # Create a vehicle.
        vehicle = Vehicle.objects.create(
            carrier=carrier,
            truck_number=f"TRK{fake.random_number(digits=3)}",
            trailer_number=f"TRL{fake.random_number(digits=3)}",
            vin=fake.vin(),
        )
        self.stdout.write(self.style.SUCCESS(f"Created vehicle {vehicle}"))

        # Patch the stop calculation functions.
        # IMPORTANT: Adjust the import path if your stop functions reside elsewhere.
        try:
            from trucker import services

            services.calculate_fuel_stops = generate_fuel_stops
            services.calculate_rest_stops = generate_rest_stops
            self.stdout.write(self.style.SUCCESS("Patched stop calculation functions"))
        except ImportError:
            self.stdout.write(
                self.style.WARNING("Could not patch stop calculation functions")
            )

        # Create multiple trips.
        for i in range(1, num_trips + 1):
            trip = self.create_trip(driver, vehicle, i)
            self.stdout.write(self.style.SUCCESS(f"Created trip {i}: {trip}"))

        self.stdout.write(self.style.SUCCESS("Dummy data generation complete!"))

    def create_trip(self, driver, vehicle, trip_num):
        """Create a complete trip with logs, stops, and duty statuses."""
        start_time = timezone.now() - timedelta(days=trip_num * 2)
        end_time = start_time + timedelta(hours=random.randint(20, 50))

        # Create a trip.
        trip = Trip.objects.create(
            driver=driver,
            vehicle=vehicle,
            current_location=fake.city() + ", " + fake.state_abbr(),
            pickup_location=fake.city() + ", " + fake.state_abbr(),
            dropoff_location=fake.city() + ", " + fake.state_abbr(),
            distance=random.randint(500, 2500),
            estimated_duration=timedelta(hours=random.randint(20, 50)),
            average_speed=random.randint(50, 65),
            start_time=start_time,
            completed_at=end_time if random.choice([True, False]) else None,
        )

        start_odo = random.randint(100000, 500000)
        end_odo = start_odo + random.randint(50, 500)  

        log_entry = LogEntry.objects.create(
            driver=driver,
            vehicle=vehicle,
            date=start_time.date(),
            start_odometer=start_odo,
            end_odometer=end_odo,
            signature=driver.user.get_full_name(),
            remarks=f"Trip #{trip_num} from {trip.pickup_location} to {trip.dropoff_location}",
            adverse_conditions=random.choice([True, False])
        )

        # Create duty statuses for the log entry.
        statuses = []
        current_time = start_time
        while current_time < end_time:
            status = random.choice(["D", "ON", "OFF", "SB"])
            duration = random.randint(1, 8) if status == "D" else random.randint(1, 4)
            statuses.append(
                DutyStatus(
                    log_entry=log_entry,
                    status=status,
                    start_time=current_time,
                    end_time=current_time + timedelta(hours=duration),
                    location_lat=random.uniform(
                        24.0, 49.0
                    ),  # approximate bounds for continental US
                    location_lon=random.uniform(-125.0, -67.0),
                    location_name=fake.city() + ", " + fake.state_abbr(),
                )
            )
            current_time += timedelta(hours=duration)
        DutyStatus.objects.bulk_create(statuses)

        return trip
