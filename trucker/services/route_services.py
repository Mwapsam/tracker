import requests
from django.conf import settings
from django.utils import timezone


def calculate_route_distance(current_location, pickup_location, dropoff_location):
    """
    Calculate route distance and duration using Google Maps Directions API
    Returns: (distance_in_miles, duration_timedelta)
    """
    api_key = settings.MAPS_API_KEY
    base_url = "https://maps.googleapis.com/maps/api/directions/json"

    params = {
        "origin": current_location,
        "destination": dropoff_location,
        "waypoints": f"via:{pickup_location}" if pickup_location else None,
        "key": api_key,
        "units": "imperial",
        "optimizeWaypoints": "true",
    }

    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data["status"] != "OK":
            raise ValueError(f"API Error: {data.get('error_message', 'Unknown error')}")

        route = data["routes"][0]
        total_distance = sum(
            leg["distance"]["value"] for leg in route["legs"]
        )  
        total_duration = sum(
            leg["duration"]["value"] for leg in route["legs"]
        )  

        return (
            total_distance / 1609.34,  
            timezone.timedelta(seconds=total_duration),
        )

    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Network error: {str(e)}") from e
    except (KeyError, IndexError) as e:
        raise ValueError("Invalid API response format") from e
