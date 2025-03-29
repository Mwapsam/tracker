import requests
import re
from django.conf import settings


def calculate_route_distance(pickup_location, dropoff_location, mode="driving"):
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
            raw_distance = data["rows"][0]["elements"][0]["distance"]["text"]
            distance = float(
                re.sub(r"[^\d.]", "", raw_distance)
            ) 

            raw_duration = data["rows"][0]["elements"][0]["duration"]["text"]
            duration_match = re.search(r"(\d+)", raw_duration) 
            duration_hours = (
                int(duration_match.group(1)) if duration_match else 0
            ) 

            return distance, duration_hours
        except KeyError:
            return "Error: Could not retrieve distance data."
    else:
        return f"Error: {data.get('error_message', 'Request failed')}"
