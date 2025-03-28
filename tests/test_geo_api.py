import timeit
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, Mock
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone

from trucker.models import Trip
from trucker.services.stop_services import (
    RouteCalculator,
    calculate_fuel_stops,
    calculate_rest_stops,
)

API_KEY = settings.MAPS_API_KEY


@pytest.fixture
def calculator():
    return RouteCalculator(API_KEY)


@pytest.fixture
def mock_google_response():
    mock_google_response = {
        "routes": [
            {
                "legs": [
                    {
                        "distance": {
                            "value": 160934
                        }, 
                        "duration": {"value": 7200}, 
                    }
                ],
                "overview_polyline": {"points": "_p~iF~ps|U_ulLnnqC_mqNvxq`@"},
            }
        ],
        "status": "OK",
    }

    return mock_google_response


@pytest.fixture
def mock_places_response():
    mock_places_response = {
        "results": [
            {
                "name": "Test Station",
                "geometry": {"location": {"lat": 34.0522, "lng": -118.2437}},
            }
        ],
        "status": "OK",
    }

    return mock_places_response


def test_get_route_details(mock_google_response):
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = mock_google_response

        calculator = RouteCalculator("fake-key")
        result = calculator.get_route_details("Origin", "Destination")

        assert result["distance"] == 100
        assert result["duration"] == 2
        assert len(result["waypoints"]) > 0


def test_calculate_fuel_stops(mock_google_response, mock_places_response):
    with patch("requests.get") as mock_get:
        mock_get.side_effect = [
            Mock(json=Mock(return_value=mock_google_response)),
            Mock(json=Mock(return_value=mock_places_response)),
        ]

        stops = calculate_fuel_stops(
            total_miles=1000,
            start_time=timezone.now(),
            origin="Origin",
            destination="Destination",
            api_key="fake-key",
        )

        assert len(stops) == 1
        assert stops[0]["location_name"] == "Test Station"
        assert stops[0]["duration"] == timedelta(minutes=30)


@pytest.fixture
def mock_rest_stop_response():
    return {
        "results": [
            {
                "name": "Rest Area",
                "geometry": {"location": {"lat": 35.1234, "lng": -119.5678}},
            }
        ],
        "status": "OK",
    }


def test_rest_stop_calculation(mock_google_response, mock_rest_stop_response):
    with patch("requests.get") as mock_get:
        mock_get.side_effect = [
            Mock(json=Mock(return_value=mock_google_response)),
            Mock(json=Mock(return_value=mock_rest_stop_response)),
            Mock(json=Mock(return_value=mock_rest_stop_response)),
        ]

        stops = calculate_rest_stops(
            total_miles=500,
            start_time=timezone.now(),
            origin="Origin",
            destination="Destination",
            api_key="fake-key",
            max_drive_hours=4,
            avg_speed=50,
        )
        assert len(stops) == 2


def test_no_stops_needed(mock_google_response):
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = mock_google_response

        calculator = RouteCalculator("fake-key")
        route = calculator.get_route_details("A", "B")

        fuel_stops = calculator.calculate_fuel_stops(
            origin="A", destination="B", start_time=timezone.now(), route=route
        )
        assert len(fuel_stops) == 0

        rest_stops = calculate_rest_stops(
            total_miles=150,
            start_time=timezone.now(),
            origin="A",
            destination="B",
            api_key="fake-key",
            max_drive_hours=4,
            avg_speed=50,
        )
        assert len(rest_stops) == 0


def test_stop_validation():
    naive_time = datetime.now().replace(tzinfo=None)
    valid_stop = {
        "stop_type": "FUEL",
        "location_name": "Station",
        "location_lat": 34.0522,
        "location_lon": -118.2437,
        "scheduled_time": naive_time,
        "duration": timedelta(minutes=30),
    }

    trip = Trip(
        pickup_location="34.0522,-118.2437",
        dropoff_location="36.7783,-119.4179",
        current_location="34.0522,-118.2437",
        start_time=naive_time,
    )

    try:
        trip.validate_stop_data(valid_stop, "FUEL")
    except ValidationError:
        pytest.fail("Validation failed for valid stop data")

    invalid_stop = valid_stop.copy()
    del invalid_stop["location_name"]
    with pytest.raises(ValidationError):
        trip.validate_stop_data(invalid_stop, "FUEL")


def test_decode_polyline(calculator):
    encoded_poly = "_p~iF~ps|U_ulLnnqC_mqNvxq`@"
    decoded = calculator._decode_polyline(encoded_poly)
    assert len(decoded) == 3
    assert pytest.approx(decoded[0]["lat"], rel=1e-1) == 37.77
    assert pytest.approx(decoded[0]["lng"], rel=1e-1) == -122.41


def test_performance(mock_google_response):
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = mock_google_response

        execution_time = timeit.timeit(
            lambda: RouteCalculator("fake-key").get_route_details("A", "B"), number=10
        )
        assert execution_time < 0.1
        print(f"Mocked execution time: {execution_time:.4f}s")
