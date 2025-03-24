from datetime import timedelta
from django.core.exceptions import ValidationError


def generate_hos_logs(trip):
    driver = trip.driver
    cycle_hours = 70 if driver.carrier.hos_cycle_choice == "70" else 60
    remaining_hours = max(cycle_hours - driver.current_cycle_used, 0)

    logs = []
    current_time = trip.start_time
    total_driving = 0
    duty_window_start = current_time
    break_accumulator = 0

    while total_driving < trip.estimated_duration.total_seconds() / 3600:
        if remaining_hours <= 0:
            raise ValidationError("Driver exceeds cycle hours - requires 34hr restart")

        if (current_time - duty_window_start).total_seconds() / 3600 >= 14:
            current_time = duty_window_start + timedelta(hours=14)
            logs.append(create_off_duty_log(current_time, 10))
            duty_window_start = current_time + timedelta(hours=10)
            current_time = duty_window_start
            continue

        max_drive_segment = min(
            11 - (driver.current_cycle_used % 11),
            remaining_hours,
            trip.estimated_duration.total_seconds() / 3600 - total_driving,
            14 - (current_time - duty_window_start).total_seconds() / 3600,
        )

        drive_end = current_time + timedelta(hours=max_drive_segment)
        logs.append(
            {
                "log_entry": trip.log_entry,
                "status": "D",
                "start_time": current_time,
                "end_time": drive_end,
                "location_name": "En route",
            }
        )

        total_driving += max_drive_segment
        driver.current_cycle_used += max_drive_segment
        remaining_hours -= max_drive_segment
        current_time = drive_end
        break_accumulator += max_drive_segment

        if break_accumulator >= 8:
            break_time = current_time + timedelta(minutes=30)
            logs.append(
                {
                    "log_entry": trip.log_entry,
                    "status": "OFF",
                    "start_time": current_time,
                    "end_time": break_time,
                    "location_name": "Rest break",
                }
            )
            current_time = break_time
            break_accumulator = 0

    driver.save()
    return logs


def create_off_duty_log(start_time, hours):
    return {
        "log_entry": None,  
        "status": "OFF",
        "start_time": start_time,
        "end_time": start_time + timedelta(hours=hours),
        "location_name": "Mandatory rest",
    }
