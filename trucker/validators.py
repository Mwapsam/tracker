from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta


def validate_overlapping_statuses(statuses, current_status):
    overlaps = current_status.__class__.objects.filter(
        log_entry=current_status.log_entry,
        start_time__lt=current_status.end_time,
        end_time__gt=current_status.start_time,
    ).exclude(pk=current_status.pk)
    if overlaps.exists():
        raise ValidationError("Duty status periods cannot overlap")


def validate_14_hour_duty_window(statuses, adverse_conditions):
    on_duty_statuses = [s for s in statuses if s.status in ["D", "ON"]]
    if on_duty_statuses:
        earliest_start = min(s.start_time for s in on_duty_statuses)
        latest_end = max(s.end_time for s in on_duty_statuses)
        window_duration = (latest_end - earliest_start).total_seconds() / 3600
        if window_duration > 14 and not adverse_conditions:
            raise ValidationError(
                "14-hour duty window exceeded without adverse conditions exception"
            )


def validate_11_hour_driving_limit(statuses):
    driving_statuses = [s for s in statuses if s.status == "D"]
    total_driving = sum(s.duration for s in driving_statuses)
    if total_driving > 11:
        raise ValidationError(
            "Driving time exceeds 11-hour limit within 14-hour window"
        )


def validate_30_minute_break(statuses):
    cumulative_driving = 0.0
    for s in statuses:
        if s.status == "D":
            cumulative_driving += round(s.duration, 2)
        elif s.status in ["OFF", "SB"]:
            if round(s.duration, 2) >= 0.5:
                cumulative_driving = 0.0
        if cumulative_driving > 8:
            raise ValidationError("30-minute break required after 8 hours of driving")


def check_34_hour_restart(current_status):
    if current_status.status in ["OFF", "SB"] and current_status.duration >= 34:
        thirty_four_hours_ago = current_status.end_time - timezone.timedelta(hours=34)
        overlapping_statuses = current_status.__class__.objects.filter(
            log_entry__driver=current_status.log_entry.driver,
            start_time__lt=current_status.end_time,
            end_time__gt=thirty_four_hours_ago,
        ).exclude(status__in=["OFF", "SB"])
        if not overlapping_statuses.exists():
            driver = current_status.log_entry.driver
            driver.last_34hr_restart = current_status.end_time
            driver.save()


def validate_sleeper_berth(statuses):
    sb_periods = [s for s in statuses if s.status == "SB"]

    if any((s.end_time - s.start_time).total_seconds() < 7 * 3600 for s in sb_periods):
        raise ValidationError("Sleeper berth periods must be at least 7 hours")


def validate_stop_data(self, stop_data: dict, expected_type: str) -> dict:
    required_fields = {
        "location_name": str,
        "location_lat": float,
        "location_lon": float,
        "scheduled_time": (datetime, timezone.datetime),
        "duration": (timedelta, timezone.timedelta),
    }

    if stop_data.get("stop_type", "") != expected_type:
        raise ValidationError(
            f"Invalid stop_type: {stop_data.get('stop_type')}. Expected {expected_type}"
        )

    for field, field_type in required_fields.items():
        if field not in stop_data:
            raise ValidationError(f"Missing required field: {field}")

        if not isinstance(stop_data[field], field_type):
            raise ValidationError(
                f"Invalid type for {field}. Expected {field_type}, got {type(stop_data[field])}"
            )

    if isinstance(stop_data["scheduled_time"], datetime):
        stop_data["scheduled_time"] = timezone.make_aware(stop_data["scheduled_time"])

    if not (-90 <= stop_data["location_lat"] <= 90):
        raise ValidationError(f"Invalid latitude: {stop_data['location_lat']}")

    if not (-180 <= stop_data["location_lon"] <= 180):
        raise ValidationError(f"Invalid longitude: {stop_data['location_lon']}")

    return stop_data
