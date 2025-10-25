import httpx
import asyncio
from typing import Optional, Dict, List, Tuple
from decimal import Decimal
import os

from app.config import settings


class GoogleMapsService:
    """Service for Google Maps API integration"""
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
        self.base_url = "https://maps.googleapis.com/maps/api"
    
    async def calculate_distance_and_duration(
        self, 
        origin_lat: float, 
        origin_lng: float, 
        destination_lat: float, 
        destination_lng: float,
        mode: str = "driving"
    ) -> Optional[Dict]:
        """
        Calculate distance and estimated travel time between two points
        
        Args:
            origin_lat, origin_lng: Starting coordinates
            destination_lat, destination_lng: Destination coordinates
            mode: Travel mode (driving, walking, transit)
        
        Returns:
            Dict with distance (meters), duration (seconds), and ETA
        """
        if not self.api_key:
            return None
        
        url = f"{self.base_url}/distancematrix/json"
        params = {
            "origins": f"{origin_lat},{origin_lng}",
            "destinations": f"{destination_lat},{destination_lng}",
            "mode": mode,
            "key": self.api_key
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if data["status"] == "OK" and data["rows"]:
                    element = data["rows"][0]["elements"][0]
                    if element["status"] == "OK":
                        return {
                            "distance": element["distance"]["value"],  # meters
                            "duration": element["duration"]["value"],  # seconds
                            "distance_text": element["distance"]["text"],
                            "duration_text": element["duration"]["text"],
                            "eta": self._calculate_eta(element["duration"]["value"])
                        }
        except Exception as e:
            print(f"Error calculating distance: {e}")
            return None
        
        return None
    
    async def get_route_directions(
        self, 
        origin_lat: float, 
        origin_lng: float, 
        destination_lat: float, 
        destination_lng: float,
        waypoints: Optional[List[Tuple[float, float]]] = None
    ) -> Optional[Dict]:
        """
        Get detailed route directions between two points
        
        Args:
            origin_lat, origin_lng: Starting coordinates
            destination_lat, destination_lng: Destination coordinates
            waypoints: Optional list of waypoint coordinates
        
        Returns:
            Dict with route details, polyline, and step-by-step directions
        """
        if not self.api_key:
            return None
        
        url = f"{self.base_url}/directions/json"
        params = {
            "origin": f"{origin_lat},{origin_lng}",
            "destination": f"{destination_lat},{destination_lng}",
            "key": self.api_key
        }
        
        if waypoints:
            waypoint_str = "|".join([f"{lat},{lng}" for lat, lng in waypoints])
            params["waypoints"] = waypoint_str
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if data["status"] == "OK" and data["routes"]:
                    route = data["routes"][0]
                    leg = route["legs"][0]
                    
                    return {
                        "distance": leg["distance"]["value"],
                        "duration": leg["duration"]["value"],
                        "distance_text": leg["distance"]["text"],
                        "duration_text": leg["duration"]["text"],
                        "polyline": route["overview_polyline"]["points"],
                        "steps": [
                            {
                                "instruction": step["html_instructions"],
                                "distance": step["distance"]["value"],
                                "duration": step["duration"]["value"],
                                "start_location": step["start_location"],
                                "end_location": step["end_location"]
                            }
                            for step in leg["steps"]
                        ]
                    }
        except Exception as e:
            print(f"Error getting directions: {e}")
            return None
        
        return None
    
    async def geocode_address(self, address: str) -> Optional[Dict]:
        """
        Convert address to coordinates
        
        Args:
            address: Address string
        
        Returns:
            Dict with lat, lng, and formatted address
        """
        if not self.api_key:
            return None
        
        url = f"{self.base_url}/geocode/json"
        params = {
            "address": address,
            "key": self.api_key
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if data["status"] == "OK" and data["results"]:
                    result = data["results"][0]
                    location = result["geometry"]["location"]
                    
                    return {
                        "lat": location["lat"],
                        "lng": location["lng"],
                        "formatted_address": result["formatted_address"],
                        "place_id": result["place_id"]
                    }
        except Exception as e:
            print(f"Error geocoding address: {e}")
            return None
        
        return None
    
    async def reverse_geocode(self, lat: float, lng: float) -> Optional[Dict]:
        """
        Convert coordinates to address
        
        Args:
            lat, lng: Coordinates
        
        Returns:
            Dict with formatted address and components
        """
        if not self.api_key:
            return None
        
        url = f"{self.base_url}/geocode/json"
        params = {
            "latlng": f"{lat},{lng}",
            "key": self.api_key
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if data["status"] == "OK" and data["results"]:
                    result = data["results"][0]
                    
                    return {
                        "formatted_address": result["formatted_address"],
                        "place_id": result["place_id"],
                        "address_components": result["address_components"]
                    }
        except Exception as e:
            print(f"Error reverse geocoding: {e}")
            return None
        
        return None
    
    async def find_nearby_places(
        self, 
        lat: float, 
        lng: float, 
        radius: int = 1000, 
        place_type: str = "bus_station"
    ) -> Optional[List[Dict]]:
        """
        Find nearby places (bus stations, restaurants, etc.)
        
        Args:
            lat, lng: Center coordinates
            radius: Search radius in meters
            place_type: Type of place to search for
        
        Returns:
            List of nearby places with details
        """
        if not self.api_key:
            return None
        
        url = f"{self.base_url}/place/nearbysearch/json"
        params = {
            "location": f"{lat},{lng}",
            "radius": radius,
            "type": place_type,
            "key": self.api_key
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if data["status"] == "OK":
                    return [
                        {
                            "name": place["name"],
                            "place_id": place["place_id"],
                            "location": place["geometry"]["location"],
                            "rating": place.get("rating"),
                            "vicinity": place.get("vicinity"),
                            "types": place.get("types", [])
                        }
                        for place in data["results"]
                    ]
        except Exception as e:
            print(f"Error finding nearby places: {e}")
            return None
        
        return None
    
    def _calculate_eta(self, duration_seconds: int) -> str:
        """Calculate ETA string from duration in seconds"""
        import datetime
        eta = datetime.datetime.now() + datetime.timedelta(seconds=duration_seconds)
        return eta.strftime("%H:%M")
    
    def calculate_distance_simple(
        self, 
        lat1: float, 
        lng1: float, 
        lat2: float, 
        lng2: float
    ) -> float:
        """
        Calculate simple distance between two points using Haversine formula
        Returns distance in kilometers
        """
        import math
        
        # Convert to radians
        lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Radius of earth in kilometers
        r = 6371
        
        return c * r


# Global instance
maps_service = GoogleMapsService()
