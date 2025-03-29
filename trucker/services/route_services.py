import requests
from django.conf import settings
from django.utils import timezone


def calculate_route_distance(
    pickup_location, dropoff_location, mode="driving"
):
    api_key = settings.MAPS_API_KEY

    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": pickup_location,
        "destinations": dropoff_location,
        "mode": mode,
        "key": api_key,
    }

    response = requests.get(url, params=params)
    data = response.json()

    if response.status_code == 200 and data["status"] == "OK":
        try:
            distance = data["rows"][0]["elements"][0]["distance"]["text"]
            duration = data["rows"][0]["elements"][0]["duration"]["text"]
            return distance, duration
        except KeyError:
            return "Error: Could not retrieve distance data."
    else:
        return f"Error: {data.get('error_message', 'Request failed')}"
