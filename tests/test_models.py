from django.db import IntegrityError
import pytest
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from trucker.models import (
    Carrier,
    Driver,
    Vehicle,
    LogEntry,
    DutyStatus,
    CycleCalculation,
)


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="testdriver",
        password="testpass123",
        first_name="John",
        last_name="Doe",
    )


@pytest.fixture
def carrier(db):
    return Carrier.objects.create(
        name="Test Carrier",
        mc_number="MC123456",
        main_office_address="123 Main St",
        home_terminal_address="456 Terminal Rd",
        hos_cycle_choice="70",
    )


@pytest.fixture
def driver(db, user, carrier):
    return Driver.objects.create(
        user=user,
        license_number="DL123456",
        carrier=carrier,
    )


@pytest.fixture
def vehicle(db, carrier):
    return Vehicle.objects.create(
        carrier=carrier,
        truck_number="TRUCK123",
        trailer_number="TRAILER456",
        vin="1ABCD23EFGH456789",
    )


@pytest.fixture
def log_entry(db, driver, vehicle):
    now = timezone.localtime()
    return LogEntry.objects.create(
        driver=driver,
        vehicle=vehicle,
        date=now.date(),
        start_odometer=1000.0,
        end_odometer=1200.5,
        signature="John Doe",
        adverse_conditions=False,
    )


@pytest.fixture
def duty_status(db, log_entry):
    now = timezone.now()
    return DutyStatus.objects.create(
        log_entry=log_entry,
        status="D",
        start_time=now,
        end_time=now + timedelta(hours=2),
        location_lat=34.0522,
        location_lon=-118.2437,
        location_name="Los Angeles, CA",
    )


@pytest.fixture
def cycle_calculation(db, driver):
    return CycleCalculation.objects.create(
        driver=driver,
        calculation_date=timezone.now().date(),
        total_hours=50.0,
        cycle_type="70-hour",
    )


def test_carrier_str(carrier):
    assert str(carrier) == "Test Carrier (MC#MC123456)"


def test_driver_str(driver):
    assert str(driver) == "John Doe (DL123456)"


def test_driver_remaining_hours(driver):
    assert driver.remaining_hours() == 70.0
    driver.current_cycle_used = 65.0
    assert driver.remaining_hours() == 5.0


def test_vehicle_str(vehicle):
    assert str(vehicle) == "TRUCK123 - TRAILER456"


def test_log_entry_total_miles(log_entry):
    assert log_entry.total_miles == 200.5


def test_duty_status_duration(duty_status):
    assert duty_status.duration == pytest.approx(2.0, rel=1e-6)


def test_duty_status_overlap_prevention(db, log_entry):
    start = timezone.now()
    end = start + timedelta(hours=2)
    status1 = DutyStatus.objects.create(
        log_entry=log_entry,
        status="D",
        start_time=start,
        end_time=end,
        location_lat=34.0522,
        location_lon=-118.2437,
        location_name="LA",
    )
    overlapping = DutyStatus(
        log_entry=log_entry,
        status="OFF",
        start_time=start + timedelta(hours=1),
        end_time=end + timedelta(hours=1),
        location_lat=34.0522,
        location_lon=-118.2437,
        location_name="LA",
    )
    with pytest.raises(ValidationError):
        overlapping.full_clean()


def test_cycle_calculation_unique(db, driver):
    date = timezone.now().date()
    CycleCalculation.objects.create(
        driver=driver, calculation_date=date, total_hours=50.0, cycle_type="70-hour"
    )
    with pytest.raises(Exception):  
        CycleCalculation.objects.create(
            driver=driver, calculation_date=date, total_hours=60.0, cycle_type="70-hour"
        )


def test_sleeper_berth_split_validation(db, log_entry):
    sb1 = DutyStatus.objects.create(
        log_entry=log_entry,
        status="SB",
        start_time=timezone.now(),
        end_time=timezone.now() + timedelta(hours=7),
        location_lat=34.0522,
        location_lon=-118.2437,
        location_name="Berth 1",
    )
    off_duty = DutyStatus.objects.create(
        log_entry=log_entry,
        status="OFF",
        start_time=sb1.end_time,
        end_time=sb1.end_time + timedelta(hours=3),
        location_lat=34.0522,
        location_lon=-118.2437,
        location_name="Rest",
    )
    log_entry.full_clean()


def test_34_hour_restart(driver):
    assert driver.last_34hr_restart is None
    restart_time = timezone.now() - timedelta(hours=35)
    driver.last_34hr_restart = restart_time
    driver.save()
    assert driver.last_34hr_restart == restart_time


def test_odometer_validation(db, driver, vehicle):
    today = timezone.now().date()
    log_entry = LogEntry(
        driver=driver,
        vehicle=vehicle,
        date=today,
        start_odometer=1000,
        end_odometer=900,  
        remarks="Test remark",
        signature="Test Signature",
        adverse_conditions=False,
    )
    with pytest.raises(ValidationError):
        log_entry.full_clean()


def test_overlapping_status_validation(db, log_entry):
    start = timezone.now()
    status1 = DutyStatus(
        log_entry=log_entry,
        status="D",
        start_time=start,
        end_time=start + timedelta(hours=2),
        location_name="Location A",
    )
    status1.full_clean()
    status1.save()
    status2 = DutyStatus(
        log_entry=log_entry,
        status="D",
        start_time=start + timedelta(minutes=30),
        end_time=start + timedelta(hours=3),
        location_name="Location B",
    )
    with pytest.raises(ValidationError):
        status2.full_clean()


def test_14_hour_window_validation(db, log_entry):
    start = timezone.now()
    end = start + timedelta(hours=15)
    status = DutyStatus(
        log_entry=log_entry,
        status="ON",
        start_time=start,
        end_time=end,
        location_name="Long Shift Location",
    )
    with pytest.raises(ValidationError):
        status.full_clean()


def test_11_hour_driving_limit(db, log_entry):
    now = timezone.now()
    status1 = DutyStatus(
        log_entry=log_entry,
        status="D",
        start_time=now,
        end_time=now + timedelta(hours=6),
        location_name="Driving A",
    )
    status1.full_clean()
    status1.save()
    status2 = DutyStatus(
        log_entry=log_entry,
        status="D",
        start_time=now + timedelta(hours=6, minutes=30),
        end_time=now + timedelta(hours=12, minutes=30),
        location_name="Driving B",
    )
    with pytest.raises(ValidationError):
        status2.full_clean()


def test_30_minute_break_required(db, log_entry):
    now = timezone.now()
    status1 = DutyStatus(
        log_entry=log_entry,
        status="D",
        start_time=now,
        end_time=now + timedelta(hours=8),
        location_name="Long Drive",
    )
    status1.full_clean()
    status1.save()

    status2 = DutyStatus(
        log_entry=log_entry,
        status="D",
        start_time=now + timedelta(hours=8),
        end_time=now + timedelta(hours=9),
        location_name="No Break",
    )
    with pytest.raises(ValidationError):
        status2.full_clean()


def test_valid_break_after_driving(db, log_entry):
    now = timezone.now()
    status1 = DutyStatus(
        log_entry=log_entry,
        status="D",
        start_time=now,
        end_time=now + timedelta(hours=8),
        location_name="Long Drive",
    )
    status1.full_clean()
    status1.save()
    break_status = DutyStatus(
        log_entry=log_entry,
        status="OFF",
        start_time=now + timedelta(hours=8),
        end_time=now + timedelta(hours=8, minutes=30),
        location_name="Break",
    )
    break_status.full_clean()
    break_status.save()
    status2 = DutyStatus(
        log_entry=log_entry,
        status="D",
        start_time=now + timedelta(hours=8, minutes=30),
        end_time=now + timedelta(hours=9, minutes=30),
        location_name="Post Break Drive",
    )
    status2.full_clean() 
    status2.save()


def test_cycle_calculation_unique_constraint(db, driver):
    date = timezone.now().date()
    CycleCalculation.objects.create(
        driver=driver, calculation_date=date, total_hours=50.0, cycle_type="70-hour"
    )
    with pytest.raises(IntegrityError):  
        CycleCalculation.objects.create(
            driver=driver, calculation_date=date, total_hours=60.0, cycle_type="70-hour"
        )


def test_valid_sleeper_berth_split(db, log_entry):
    now = timezone.now()
    sb1 = DutyStatus(
        log_entry=log_entry,
        status="SB",
        start_time=now,
        end_time=now + timedelta(hours=7),
        location_name="Berth 1",
    )
    sb2 = DutyStatus(
        log_entry=log_entry,
        status="SB",
        start_time=now + timedelta(hours=10),
        end_time=now + timedelta(hours=17),
        location_name="Berth 2",
    )
    sb1.full_clean()
    sb1.save()
    sb2.full_clean() 
    sb2.save()


def test_invalid_sleeper_berth_split(db, log_entry):
    now = timezone.localtime()  
    sb1 = DutyStatus(
        log_entry=log_entry,
        status="SB",
        start_time=now,
        end_time=now + timedelta(hours=3),
        location_name="Invalid Berth",
    )
    with pytest.raises(ValidationError):
        sb1.full_clean() 


def test_34_hour_restart_success(driver, log_entry):
    start = timezone.localtime() - timedelta(hours=35)
    DutyStatus.objects.create(
        log_entry=log_entry,
        status="OFF",
        start_time=start,
        end_time=start + timedelta(hours=34),
        location_name="Restart window",
    )
    assert driver.check_34hr_restart(timezone.localtime())


def test_8_day_cycle_reset(driver):
    old_date = timezone.now() - timedelta(days=9)
    CycleCalculation.objects.create(
        driver=driver, calculation_date=old_date, total_hours=65.0, cycle_type="70-hour"
    )

    assert driver.current_cycle_used == 0  


def test_cross_timezone_validation(db, log_entry):
    tz_aware_time = timezone.make_aware(timezone.datetime(2023, 1, 1, 23, 30))
    status = DutyStatus(
        log_entry=log_entry,
        status="D",
        start_time=tz_aware_time,
        end_time=tz_aware_time + timedelta(hours=2),
        location_name="Cross-day drive",
    )
    status.full_clean()  
    status.save()
