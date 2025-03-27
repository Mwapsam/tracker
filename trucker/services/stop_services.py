import polyline
import requests
from datetime import timedelta
from typing import List, Dict, Optional


class RouteCalculator:
    def __init__(self, google_maps_key: str):
        self.api_key = google_maps_key
        self.fuel_range = 1000  # miles between fuel stops

    def get_route_details(self, origin: str, destination: str) -> Dict:
        """Get complete route details including polyline, distance and duration."""
        url = "https://maps.googleapis.com/maps/api/directions/json"
        params = {
            "origin": origin,
            "destination": destination,
            "key": self.api_key,
            "mode": "driving",
            "alternatives": False,
            "units": "imperial",
        }

        response = requests.get(url, params=params)
        data = response.json()
        if data["status"] != "OK":
            raise RuntimeError(
                f"Directions API error: {data.get('error_message', 'Unknown error')}"
            )

        route = data["routes"][0]
        total_distance = (
            sum(leg["distance"]["value"] for leg in route["legs"]) / 1609.34
        )  # meters to miles
        total_duration = (
            sum(leg["duration"]["value"] for leg in route["legs"]) / 3600
        )  # seconds to hours
        polyline_str = route["overview_polyline"]["points"]
        waypoints = self._decode_polyline(polyline_str)
        return {
            "polyline": polyline_str,
            "distance": total_distance,
            "duration": total_duration,
            "waypoints": waypoints,
        }

    def _decode_polyline(self, polyline_str: str) -> List[Dict]:
        """Decode an encoded polyline into a list of coordinate dictionaries."""
        return [{"lat": lat, "lng": lng} for lat, lng in polyline.decode(polyline_str)]

    def calculate_fuel_stops(
        self, origin: str, destination: str, start_time, route: Optional[Dict] = None
    ) -> List[Dict]:
        """Calculate fuel stops along the route using a nearby search for gas stations."""
        if route is None:
            route = self.get_route_details(origin, destination)

        stops = []
        total_miles = route["distance"]
        num_stops = int(total_miles // self.fuel_range)

        for i in range(1, num_stops + 1):
            target_mile = i * self.fuel_range
            waypoint = self._find_route_waypoint(
                route["waypoints"], target_mile, total_miles
            )

            station = self._find_fuel_station(waypoint)
            if station:
                station["scheduled_time"] = start_time + timedelta(
                    hours=target_mile / 50
                )  # Estimated time, adjust average speed as needed
                station["distance_from_start"] = target_mile
                stops.append(station)

        return stops

    def _find_route_waypoint(
        self, waypoints: List[Dict], target_mile: float, total_miles: float
    ) -> Dict:
        """Find an approximate waypoint corresponding to a target mile marker."""
        mile_per_point = total_miles / len(waypoints)
        index = min(int(target_mile / mile_per_point), len(waypoints) - 1)
        return waypoints[index]

    def _find_fuel_station(self, location: Dict, radius: int = 5000) -> Optional[Dict]:
        """Find the nearest fuel station to a given location using the Places API."""
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "location": f"{location['lat']},{location['lng']}",
            "radius": radius,  # in meters
            "type": "gas_station",
            "key": self.api_key,
            "rankby": "distance",
        }
        response = requests.get(url, params=params)
        data = response.json()
        if data["status"] == "OK" and data["results"]:
            station = data["results"][0]
            return {
                "stop_type": "FUEL",
                "location_name": station["name"],
                "location_lat": station["geometry"]["location"]["lat"],
                "location_lon": station["geometry"]["location"]["lng"],
                "duration": timedelta(minutes=30),
            }
        return None


def calculate_fuel_stops(
    total_miles: float, start_time, origin: str, destination: str, api_key: str
) -> List[Dict]:
    calculator = RouteCalculator(api_key)
    route = calculator.get_route_details(origin, destination)
    return calculator.calculate_fuel_stops(origin, destination, start_time, route)
