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
    return Driver.objects.create(user=user, license_number="DL123456", carrier=carrier)


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
    return LogEntry.objects.create(
        driver=driver,
        vehicle=vehicle,
        date=timezone.now().date(),
        start_odometer=1000.0,
        end_odometer=1200.5,
        duty_window_start=timezone.now(),
        signature="John Doe",
    )


@pytest.fixture
def duty_status(db, log_entry):
    return DutyStatus.objects.create(
        log_entry=log_entry,
        status="D",
        start_time=timezone.now(),
        end_time=timezone.now() + timedelta(hours=2),
        location_lat=34.0522,
        location_lon=-118.2437,
        location_name="Los Angeles, CA",
    )


def test_carrier_str(carrier):
    assert str(carrier) == "Test Carrier (MC#MC123456)"


def test_driver_str(driver):
    assert str(driver) == "John Doe (DL123456)"


def test_driver_remaining_hours(driver):
    # Initial remaining hours for 70-hour cycle
    assert driver.remaining_hours() == 70.0

    # Test after adding hours
    driver.current_cycle_used = 65.0
    assert driver.remaining_hours() == 5.0


def test_vehicle_str(vehicle):
    assert str(vehicle) == "TRUCK123 - TRAILER456"


def test_log_entry_total_miles(log_entry):
    assert log_entry.total_miles == 200.5


def test_log_entry_duty_window_validation(log_entry):
    # Valid 14-hour window
    log_entry.duty_window_end = log_entry.duty_window_start + timedelta(hours=14)
    log_entry.full_clean()  # Should not raise error

    # Invalid window without adverse conditions
    log_entry.duty_window_end += timedelta(hours=1)
    with pytest.raises(ValidationError):
        log_entry.full_clean()

    # Valid with adverse conditions
    log_entry.adverse_conditions = True
    log_entry.full_clean()  # Should pass


def test_duty_status_duration(duty_status):
    assert duty_status.duration == pytest.approx(2.0, rel=1e-6)

def test_duty_status_overlap_prevention(log_entry):
    # Create first status
    start = timezone.now()
    end = start + timedelta(hours=2)
    DutyStatus.objects.create(
        log_entry=log_entry,
        status="D",
        start_time=start,
        end_time=end,
        location_lat=34.0522,
        location_lon=-118.2437,
        location_name="LA",
    )

    # Overlapping status
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


def test_cycle_calculation_unique(driver):
    date = timezone.now().date()
    CycleCalculation.objects.create(
        driver=driver, calculation_date=date, total_hours=50.0, cycle_type="70-hour"
    )

    with pytest.raises(Exception):  # Expect IntegrityError
        CycleCalculation.objects.create(
            driver=driver, calculation_date=date, total_hours=60.0, cycle_type="70-hour"
        )


def test_sleeper_berth_split_validation(log_entry):
    # Valid 7+3 split
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
    # Test restart tracking
    assert driver.last_34hr_restart is None
    restart_time = timezone.now() - timedelta(hours=35)
    driver.last_34hr_restart = restart_time
    driver.save()

    assert driver.last_34hr_restart == restart_time
