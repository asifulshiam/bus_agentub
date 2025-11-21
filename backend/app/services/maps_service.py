"""
OpenStreetMap Integration Service
Replaces Google Maps with free OSM APIs
No API key required, no live traffic data
"""

import math
from datetime import datetime
from typing import Dict, List, Optional

import httpx


class MapsService:
    """
    OpenStreetMap-based location service
    Uses: Nominatim (geocoding), OSRM (routing), Overpass (POI)
    """

    def __init__(self):
        self.nominatim_base = "https://nominatim.openstreetmap.org"
        self.osrm_base = "https://router.project-osrm.org"
        self.overpass_base = "https://overpass-api.de/api"

        # Required headers for Nominatim (must identify your app)
        self.headers = {
            "User-Agent": "BusAgentUB/1.0 (Student Project; asiful.islam12@northsouth.edu)"
        }

    async def geocode_address(self, address: str) -> Optional[Dict]:
        """
        Convert address to coordinates using Nominatim
        Rate limit: 1 request/second

        Returns:
            {
                "lat": 23.8103,
                "lng": 90.4125,
                "display_name": "Dhaka, Bangladesh",
                "address": {...}
            }
        """
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(
                    f"{self.nominatim_base}/search",
                    params={
                        "q": address,
                        "format": "json",
                        "limit": 1,
                        "countrycodes": "bd",  # Bangladesh only
                    },
                    headers=self.headers,
                )

                if response.status_code == 200:
                    results = response.json()
                    if results:
                        result = results[0]
                        return {
                            "lat": float(result["lat"]),
                            "lng": float(result["lon"]),
                            "display_name": result["display_name"],
                            "address": result.get("address", {}),
                        }
                return None
            except Exception as e:
                print(f"Geocoding error: {e}")
                return None

    async def reverse_geocode(self, lat: float, lng: float) -> Optional[Dict]:
        """
        Convert coordinates to address using Nominatim
        Rate limit: 1 request/second

        Returns:
            {
                "display_name": "Mohakhali, Dhaka",
                "address": {
                    "road": "Mohakhali",
                    "city": "Dhaka",
                    "country": "Bangladesh"
                }
            }
        """
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(
                    f"{self.nominatim_base}/reverse",
                    params={"lat": lat, "lon": lng, "format": "json"},
                    headers=self.headers,
                )

                if response.status_code == 200:
                    return response.json()
                return None
            except Exception as e:
                print(f"Reverse geocoding error: {e}")
                return None

    def calculate_distance(
        self, lat1: float, lng1: float, lat2: float, lng2: float
    ) -> float:
        """
        Calculate distance between two points using Haversine formula
        Returns distance in kilometers
        """
        R = 6371  # Earth's radius in km

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)

        a = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    async def get_route(
        self, start_lat: float, start_lng: float, end_lat: float, end_lng: float
    ) -> Optional[Dict]:
        """
        Get route between two points using OSRM

        Returns:
            {
                "distance": 15.2,  # km
                "duration": 1800,  # seconds (30 min)
                "geometry": [...],  # route coordinates
                "steps": [...]  # turn-by-turn directions
            }
        """
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                # OSRM route API
                coords = f"{start_lng},{start_lat};{end_lng},{end_lat}"
                response = await client.get(
                    f"{self.osrm_base}/route/v1/driving/{coords}",
                    params={
                        "overview": "full",
                        "steps": "true",
                        "geometries": "geojson",
                    },
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("code") == "Ok" and data.get("routes"):
                        route = data["routes"][0]
                        return {
                            "distance": route["distance"] / 1000,  # meters to km
                            "duration": route["duration"],  # seconds
                            "geometry": route["geometry"]["coordinates"],
                            "steps": route["legs"][0].get("steps", []),
                        }
                return None
            except Exception as e:
                print(f"Route calculation error: {e}")
                return None

    async def calculate_eta(
        self, bus_lat: float, bus_lng: float, stop_lat: float, stop_lng: float
    ) -> Dict:
        """
        Calculate ETA from bus current position to boarding point
        Uses OSRM for accurate routing
        Falls back to straight-line distance if OSRM fails

        Returns:
            {
                "distance_km": 5.2,
                "eta_minutes": 15,
                "eta_time": "2025-11-16T10:30:00"
            }
        """
        # Try OSRM first for accurate route
        route = await self.get_route(bus_lat, bus_lng, stop_lat, stop_lng)

        if route:
            distance_km = route["distance"]
            duration_seconds = route["duration"]
            eta_minutes = int(duration_seconds / 60)
        else:
            # Fallback: straight-line distance
            distance_km = self.calculate_distance(bus_lat, bus_lng, stop_lat, stop_lng)
            # Assume average speed 40 km/h in city
            eta_minutes = int((distance_km / 40) * 60)

        # Calculate arrival time
        from datetime import timedelta

        eta_time = datetime.now() + timedelta(minutes=eta_minutes)

        return {
            "distance_km": round(distance_km, 2),
            "eta_minutes": eta_minutes,
            "eta_time": eta_time.isoformat(),
        }

    async def get_nearby_places(
        self, lat: float, lng: float, radius: int = 500, place_type: str = "restaurant"
    ) -> List[Dict]:
        """
        Find nearby places using Overpass API

        Args:
            lat, lng: Center coordinates
            radius: Search radius in meters (default 500m)
            place_type: Type of place (restaurant, hospital, atm, etc.)

        Returns:
            [
                {
                    "name": "Restaurant Name",
                    "lat": 23.8103,
                    "lng": 90.4125,
                    "type": "restaurant",
                    "distance_m": 250
                }
            ]
        """
        # Map common types to OSM tags
        type_mapping = {
            "restaurant": "amenity=restaurant",
            "hospital": "amenity=hospital",
            "atm": "amenity=atm",
            "pharmacy": "amenity=pharmacy",
            "fuel": "amenity=fuel",
            "hotel": "tourism=hotel",
        }

        osm_tag = type_mapping.get(place_type, f"amenity={place_type}")

        # Overpass QL query
        query = f"""
        [out:json];
        (
          node[{osm_tag}](around:{radius},{lat},{lng});
          way[{osm_tag}](around:{radius},{lat},{lng});
        );
        out center 20;
        """

        async with httpx.AsyncClient(timeout=20.0) as client:
            try:
                response = await client.get(
                    f"{self.overpass_base}/interpreter", params={"data": query}
                )

                if response.status_code == 200:
                    data = response.json()
                    places = []

                    for element in data.get("elements", [])[:20]:  # Limit to 20
                        # Get coordinates
                        if element["type"] == "node":
                            elem_lat = element["lat"]
                            elem_lng = element["lon"]
                        else:  # way
                            elem_lat = element.get("center", {}).get("lat")
                            elem_lng = element.get("center", {}).get("lon")

                        if not elem_lat or not elem_lng:
                            continue

                        # Calculate distance
                        distance = (
                            self.calculate_distance(lat, lng, elem_lat, elem_lng) * 1000
                        )  # km to m

                        places.append(
                            {
                                "name": element.get("tags", {}).get("name", "Unnamed"),
                                "lat": elem_lat,
                                "lng": elem_lng,
                                "type": place_type,
                                "distance_m": int(distance),
                                "tags": element.get("tags", {}),
                            }
                        )

                    # Sort by distance
                    places.sort(key=lambda x: x["distance_m"])
                    return places

                return []
            except Exception as e:
                print(f"Nearby places error: {e}")
                return []


# Singleton instance
maps_service = MapsService()
