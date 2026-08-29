from sqlalchemy.orm import Session
from app.models.transport import Route, Shipment, ShipmentTracking, Vehicle
from app.schemas.transport import RouteCreate, ShipmentCreate
from datetime import datetime, timedelta
from uuid import UUID
import logging
import math

logger = logging.getLogger(__name__)

class TransportService:
    async def optimize_route(self, db: Session, route: RouteCreate) -> Route:
        """Optimize route using Google Maps API"""
        # In production, integrate with Google Maps API
        # For now, create basic route
        db_route = Route(
            route_name=route.route_name,
            origin_address=route.origin_address,
            origin_lat=route.origin_lat,
            origin_lng=route.origin_lng,
            destination_address=route.destination_address,
            destination_lat=route.destination_lat,
            destination_lng=route.destination_lng,
            waypoints=route.waypoints,
            optimized=True
        )
        
        # Calculate distance (simplified Haversine formula)
        if db_route.origin_lat and db_route.destination_lat:
            db_route.distance_km = self._calculate_distance(
                db_route.origin_lat, db_route.origin_lng,
                db_route.destination_lat, db_route.destination_lng
            )
            # Estimate duration (avg 60 km/h)
            db_route.estimated_duration_minutes = int((db_route.distance_km / 60) * 60)
        
        db.add(db_route)
        db.commit()
        db.refresh(db_route)
        logger.info(f"Route optimized: {db_route.id}")
        return db_route
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates using Haversine formula"""
        R = 6371  # Earth's radius in km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def create_shipment(self, db: Session, shipment: ShipmentCreate) -> Shipment:
        """Create new shipment"""
        db_shipment = Shipment(
            shipment_number=shipment.shipment_number,
            order_id=shipment.order_id,
            route_id=shipment.route_id,
            vehicle_id=shipment.vehicle_id,
            driver_id=shipment.driver_id,
            weight_kg=shipment.weight_kg,
            volume=shipment.volume,
            scheduled_delivery=shipment.scheduled_delivery
        )
        db.add(db_shipment)
        db.commit()
        db.refresh(db_shipment)
        logger.info(f"Shipment created: {db_shipment.id}")
        return db_shipment
    
    def update_tracking(self, db: Session, shipment_id: UUID, latitude: float, longitude: float, speed_kmh: float = None) -> dict:
        """Update shipment GPS tracking"""
        tracking = ShipmentTracking(
            shipment_id=shipment_id,
            latitude=latitude,
            longitude=longitude,
            speed_kmh=speed_kmh,
            timestamp=datetime.utcnow()
        )
        db.add(tracking)
        db.commit()
        
        return {
            "shipment_id": str(shipment_id),
            "latitude": latitude,
            "longitude": longitude,
            "timestamp": tracking.timestamp
        }
    
    def check_delay_risk(self, db: Session, shipment_id: UUID) -> dict:
        """Check shipment delay risk based on current tracking and schedule"""
        shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
        if not shipment:
            return {"error": "Shipment not found"}
        
        if not shipment.scheduled_delivery:
            return {"risk": False, "reason": "No scheduled delivery date"}
        
        # Get latest tracking
        latest_tracking = db.query(ShipmentTracking).filter(
            ShipmentTracking.shipment_id == shipment_id
        ).order_by(ShipmentTracking.timestamp.desc()).first()
        
        if not latest_tracking:
            return {"risk": False, "reason": "No tracking data available"}
        
        # Simple delay detection: if we're far from destination and time is running out
        time_remaining = (shipment.scheduled_delivery - datetime.utcnow()).total_seconds() / 3600  # hours
        
        delay_risk = time_remaining < 2  # Risk if less than 2 hours remaining
        
        if delay_risk:
            shipment.delay_risk = True
            shipment.delay_reason = "Behind schedule - high risk of late delivery"
            db.commit()
        
        return {
            "shipment_id": str(shipment_id),
            "risk": delay_risk,
            "time_remaining_hours": max(0, time_remaining),
            "estimated_delivery": shipment.scheduled_delivery
        }
