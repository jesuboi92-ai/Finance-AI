from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.database import get_db
from app.models.transport import Route, Shipment, Vehicle, ShipmentTracking
from app.schemas.transport import (
    RouteCreate, RouteResponse, ShipmentCreate, ShipmentResponse, 
    ShipmentTrackingResponse, VehicleResponse
)
from app.services.transport_service import TransportService
from app.utils.security import get_current_user

router = APIRouter()
transport_service = TransportService()

@router.get("/vehicles", response_model=List[VehicleResponse])
async def get_vehicles(
    status: str = Query(None),
    skip: int = Query(0),
    limit: int = Query(10),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get available vehicles"""
    query = db.query(Vehicle)
    if status:
        query = query.filter(Vehicle.status == status)
    vehicles = query.offset(skip).limit(limit).all()
    return vehicles

@router.get("/routes", response_model=List[RouteResponse])
async def get_routes(
    status: str = Query(None),
    skip: int = Query(0),
    limit: int = Query(10),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get routes"""
    query = db.query(Route)
    if status:
        query = query.filter(Route.status == status)
    routes = query.offset(skip).limit(limit).all()
    return routes

@router.post("/routes/optimize", response_model=RouteResponse)
async def optimize_route(
    route: RouteCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Optimize route using Google Maps API"""
    optimized_route = await transport_service.optimize_route(db, route)
    return optimized_route

@router.get("/shipments", response_model=List[ShipmentResponse])
async def get_shipments(
    status: str = Query(None),
    skip: int = Query(0),
    limit: int = Query(10),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get shipments"""
    query = db.query(Shipment)
    if status:
        query = query.filter(Shipment.status == status)
    shipments = query.offset(skip).limit(limit).all()
    return shipments

@router.post("/shipments", response_model=ShipmentResponse, status_code=status.HTTP_201_CREATED)
async def create_shipment(
    shipment: ShipmentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create new shipment"""
    new_shipment = transport_service.create_shipment(db, shipment)
    return new_shipment

@router.get("/shipments/{shipment_id}/tracking", response_model=List[ShipmentTrackingResponse])
async def get_shipment_tracking(
    shipment_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get real-time shipment tracking"""
    tracking = db.query(ShipmentTracking).filter(
        ShipmentTracking.shipment_id == shipment_id
    ).order_by(ShipmentTracking.timestamp.desc()).all()
    return tracking

@router.post("/shipments/{shipment_id}/track")
async def update_tracking(
    shipment_id: UUID,
    latitude: float,
    longitude: float,
    speed_kmh: float = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update shipment GPS location"""
    result = transport_service.update_tracking(db, shipment_id, latitude, longitude, speed_kmh)
    return result

@router.post("/shipments/{shipment_id}/check-delay-risk")
async def check_delay_risk(
    shipment_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Check shipment delay risk"""
    risk = transport_service.check_delay_risk(db, shipment_id)
    return risk
