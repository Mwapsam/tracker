from datetime import timedelta
import random


def calculate_fuel_stops(total_miles, start_time):
    """Generate fuel stops with realistic coordinates"""
    stops = []
    interval = 1000
    current_mile = interval
    base_lat = 34.0522  # Starting in Los Angeles
    base_lon = -118.2437

    while current_mile < total_miles:
        stops.append(
            {
                "stop_type": "FUEL",
                "location_name": f"Fuel Stop at Mile {current_mile}",
                "location_lat": base_lat
                + (current_mile * 0.01),  # Simulate northward movement
                "location_lon": base_lon
                + (current_mile * 0.005),  # Simulate eastward movement
                "scheduled_time": start_time + timedelta(hours=current_mile / 50),
                "duration": timedelta(minutes=30),
            }
        )
        current_mile += interval
        # Add some random variation
        base_lat += random.uniform(-0.1, 0.1)
        base_lon += random.uniform(-0.1, 0.1)

    return stops


def calculate_rest_stops(total_hours, start_time):
    """Generate rest stops with realistic coordinates"""
    stops = []
    interval = 8
    current_hour = interval
    base_lat = 34.0522
    base_lon = -118.2437

    while current_hour < total_hours:
        stops.append(
            {
                "stop_type": "REST",
                "location_name": f"Rest Stop after {current_hour}h",
                "location_lat": base_lat
                + (current_hour * 0.1),  # Simulate northward movement
                "location_lon": base_lon
                + (current_hour * 0.05),  # Simulate eastward movement
                "scheduled_time": start_time + timedelta(hours=current_hour),
                "duration": timedelta(hours=10),
            }
        )
        current_hour += interval
        # Add some random variation
        base_lat += random.uniform(-0.1, 0.1)
        base_lon += random.uniform(-0.1, 0.1)

    return stops
