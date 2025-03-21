from django.core.exceptions import ValidationError
from django.utils import timezone


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
    """
    If the current status is an OFF or SB and the duration is at least 34 hours,
    then if no non-break status overlaps in the last 34 hours, update the driver's restart.
    """
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


