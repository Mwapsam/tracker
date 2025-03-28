import requests
from django.conf import settings
from django.utils import timezone


def calculate_route_distance(current_location, pickup_location, dropoff_location):
    """
    Uses the Google Maps Directions API to compute the route distance and estimated duration.
    The route is calculated from the current location, via the pickup location, to the dropoff location.
    """
    api_key = settings.MAPS_API_KEY  
    base_url = "https://maps.googleapis.com/maps/api/directions/json"

    params = {
        "origin": pickup_location,
        "destination": dropoff_location,
        "waypoints": current_location,
        "key": api_key,
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        if data.get("status") != "OK":
            raise Exception(
                "Google Maps API error: " + data.get("status", "Unknown error")
            )

        route = data["routes"][0]
        total_distance = 0
        total_duration = 0

        for leg in route["legs"]:
            total_distance += leg["distance"]["value"]  
            total_duration += leg["duration"]["value"]  

        distance_km = total_distance / 1000  
        return distance_km, timezone.timedelta(seconds=total_duration)
    else:
        raise Exception("Error fetching route data from Google Maps API")
