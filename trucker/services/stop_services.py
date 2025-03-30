import requests
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

METERS_TO_MILES = 1 / 1609.34


def get_route_steps(api_key: str, origin: str, destination: str) -> List[Dict]:
    directions_url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": origin,
        "destination": destination,
        "mode": "driving",
        "key": api_key,
    }
    response = requests.get(directions_url, params=params)
    data = response.json()
    if response.status_code != 200 or data.get("status") != "OK":
        raise Exception(data.get("error_message", "Failed to retrieve directions"))
    return data["routes"][0]["legs"][0]["steps"]


def collect_stops_by_interval(steps: List[Dict], interval_miles: int) -> List[Dict]:
    total_distance = sum(step["distance"]["value"] * METERS_TO_MILES for step in steps)
    num_stops = int(total_distance // interval_miles)

    stop_waypoints = []
    cumulative_distance = 0.0
    step_index = 0
    for stop in range(1, num_stops + 1):
        target_distance = stop * interval_miles
        while step_index < len(steps) and cumulative_distance < target_distance:
            cumulative_distance += (
                steps[step_index]["distance"]["value"] * METERS_TO_MILES
            )
            step_index += 1
        if step_index - 1 < len(steps):
            waypoint = steps[step_index - 1]["end_location"]
            stop_waypoints.append({"lat": waypoint["lat"], "lng": waypoint["lng"]})
    return stop_waypoints


def query_places(
    api_key: str,
    waypoint: Dict,
    place_type: str,
    radius: int = 5000,
    max_results: int = 3,
) -> List[Dict]:
    places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{waypoint['lat']},{waypoint['lng']}",
        "radius": radius,
        "type": place_type,
        "key": api_key,
    }
    response = requests.get(places_url, params=params)
    data = response.json()
    if data.get("status") == "OK":
        return data.get("results", [])[:max_results]
    return []


def get_stops_concurrently(
    api_key: str, origin: str, destination: str, interval_miles: int, place_type: str
) -> List[Dict]:
    steps = get_route_steps(api_key, origin, destination)
    waypoints = collect_stops_by_interval(steps, interval_miles)

    stops_by_waypoint = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_waypoint = {
            executor.submit(query_places, api_key, waypoint, place_type): waypoint
            for waypoint in waypoints
        }
        for future in as_completed(future_to_waypoint):
            waypoint = future_to_waypoint[future]
            try:
                raw_stops = future.result()
            except Exception as exc:
                raw_stops = []
                print(f"Waypoint {waypoint} generated an exception: {exc}")
            stops_by_waypoint.append({"waypoint": waypoint, "stations": raw_stops})
    return stops_by_waypoint


def get_fueling_stations(
    api_key: str, origin: str, destination: str, interval_miles: int = 1000
) -> List[Dict]:
    return get_stops_concurrently(
        api_key, origin, destination, interval_miles, place_type="gas_station"
    )


def get_rest_stops(
    api_key: str, origin: str, destination: str, interval_miles: int = 1000
) -> List[Dict]:
    return get_stops_concurrently(
        api_key, origin, destination, interval_miles, place_type="rest_stop"
    )


def map_stop_data(raw_station: dict, duration: str, stop_type: str) -> dict:
    return {
        "location_name": raw_station.get("name"),
        "location_lat": raw_station.get("geometry", {}).get("location", {}).get("lat"),
        "location_lon": raw_station.get("geometry", {}).get("location", {}).get("lng"),
        "duration": duration,
        "stop_type": stop_type,
    }


def flatten_and_map(raw_data: List[Dict], duration: str, stop_type: str) -> List[Dict]:
    mapped_stops = []
    for waypoint_data in raw_data:
        stations = waypoint_data.get("stations", [])
        for station in stations:
            mapped_stops.append(map_stop_data(station, duration, stop_type))
    return mapped_stops
