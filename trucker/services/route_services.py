import re
import requests
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
            distance = data["rows"][0]["elements"][0]["distance"]["text"]
            duration_text = data["rows"][0]["elements"][0]["duration"]["text"]

            hours = 0
            minutes = 0
            match = re.search(r"(\d+)\s*hour", duration_text)
            if match:
                hours = int(match.group(1))

            match = re.search(r"(\d+)\s*min", duration_text)
            if match:
                minutes = int(match.group(1))

            total_duration = hours + (minutes / 60)

            return distance, total_duration
        except KeyError:
            return "Error: Could not retrieve distance data."
    else:
        return f"Error: {data.get('error_message', 'Request failed')}"
