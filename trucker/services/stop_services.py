from datetime import timedelta


def calculate_fuel_stops(total_miles, start_time):
    stops = []
    interval = 1000  
    current_mile = interval
    time_per_1000_miles = timedelta(hours=1000 / 50)  

    while current_mile < total_miles:
        stops.append(
            {
                "stop_type": "FUEL",
                "location_name": f"Fuel Stop at Mile {current_mile}",
                "scheduled_time": start_time
                + time_per_1000_miles * (current_mile / 1000),
                "duration": timedelta(minutes=30),
            }
        )
        current_mile += interval

    return stops


def calculate_rest_stops(total_hours, start_time):
    stops = []
    interval = 8 
    current_hour = interval

    while current_hour < total_hours:
        stops.append(
            {
                "stop_type": "REST",
                "location_name": f"Rest Stop after {current_hour}h",
                "scheduled_time": start_time + timedelta(hours=current_hour),
                "duration": timedelta(hours=10),
            }
        )
        current_hour += interval

    return stops
