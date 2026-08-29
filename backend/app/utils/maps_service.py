"""Google Maps integration for route optimization"""
import googlemaps
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class MapsService:
    def __init__(self):
        if settings.GOOGLE_MAPS_API_KEY:
            self.gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
        else:
            self.gmaps = None
    
    def get_distance_matrix(self, origins: list, destinations: list) -> dict:
        """Get distance matrix between multiple locations"""
        if not self.gmaps:
            logger.warning("Google Maps API key not configured")
            return None
        
        try:
            result = self.gmaps.distance_matrix(origins, destinations)
            return result
        except Exception as e:
            logger.error(f"Error getting distance matrix: {e}")
            return None
    
    def get_directions(self, origin: str, destination: str, waypoints: list = None) -> dict:
        """Get directions and route information"""
        if not self.gmaps:
            logger.warning("Google Maps API key not configured")
            return None
        
        try:
            result = self.gmaps.directions(
                origin=origin,
                destination=destination,
                waypoints=waypoints,
                optimize_waypoints=True if waypoints else False
            )
            return result
        except Exception as e:
            logger.error(f"Error getting directions: {e}")
            return None
    
    def geocode(self, address: str) -> dict:
        """Geocode address to coordinates"""
        if not self.gmaps:
            logger.warning("Google Maps API key not configured")
            return None
        
        try:
            result = self.gmaps.geocode(address)
            if result:
                location = result[0]['geometry']['location']
                return {
                    "latitude": location['lat'],
                    "longitude": location['lng']
                }
            return None
        except Exception as e:
            logger.error(f"Error geocoding address: {e}")
            return None

maps_service = MapsService()
