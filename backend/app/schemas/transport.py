from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class VehicleBase(BaseModel):
    license_plate: str
    vehicle_type: str
    brand: str
    model: str
    capacity_kg: float

class VehicleCreate(VehicleBase):
    capacity_volume: Optional[float] = None
    year: Optional[int] = None
    fuel_type: Optional[str] = None

class VehicleResponse(VehicleBase):
    id: UUID
    status: str
    driver_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RouteBase(BaseModel):
    route_name: str
    origin_address: str
    destination_address: str

class RouteCreate(RouteBase):
    origin_lat: Optional[float] = None
    origin_lng: Optional[float] = None
    destination_lat: Optional[float] = None
    destination_lng: Optional[float] = None
    waypoints: Optional[List[Dict[str, Any]]] = None

class RouteResponse(RouteBase):
    id: UUID
    distance_km: Optional[float]
    estimated_duration_minutes: Optional[int]
    status: str
    optimized: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ShipmentBase(BaseModel):
    shipment_number: str
    status: str = "pending"

class ShipmentCreate(ShipmentBase):
    order_id: Optional[UUID] = None
    route_id: Optional[UUID] = None
    vehicle_id: Optional[UUID] = None
    driver_id: Optional[UUID] = None
    weight_kg: Optional[float] = None
    volume: Optional[float] = None
    scheduled_delivery: Optional[datetime] = None

class ShipmentResponse(ShipmentBase):
    id: UUID
    delay_risk: bool
    delay_reason: Optional[str]
    actual_delivery: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class ShipmentTrackingResponse(BaseModel):
    id: UUID
    shipment_id: UUID
    latitude: float
    longitude: float
    timestamp: datetime
    status: Optional[str]
    speed_kmh: Optional[float]
