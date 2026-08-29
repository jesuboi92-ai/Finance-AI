from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.dialects.postgresql import UUID, JSON
from datetime import datetime
import uuid
from app.database import Base

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    license_plate = Column(String(50), unique=True, nullable=False, index=True)
    vehicle_type = Column(String(50), nullable=False)  # van, truck, car, motorcycle
    brand = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    capacity_kg = Column(Float, nullable=False)
    capacity_volume = Column(Float, nullable=True)  # in cubic meters
    year = Column(Integer, nullable=True)
    status = Column(String(50), default="available")  # available, in_use, maintenance, retired
    driver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    gps_enabled = Column(Boolean, default=True)
    last_maintenance = Column(DateTime, nullable=True)
    fuel_type = Column(String(50), nullable=True)  # diesel, petrol, electric, hybrid
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Route(Base):
    __tablename__ = "routes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    route_name = Column(String(100), nullable=False)
    origin_address = Column(Text, nullable=False)
    origin_lat = Column(Float, nullable=True)
    origin_lng = Column(Float, nullable=True)
    destination_address = Column(Text, nullable=False)
    destination_lat = Column(Float, nullable=True)
    destination_lng = Column(Float, nullable=True)
    waypoints = Column(JSON, nullable=True)  # Array of waypoints
    distance_km = Column(Float, nullable=True)
    estimated_duration_minutes = Column(Integer, nullable=True)
    status = Column(String(50), default="planned")  # planned, in_progress, completed, cancelled
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=True)
    optimized = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Shipment(Base):
    __tablename__ = "shipments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shipment_number = Column(String(100), unique=True, nullable=False, index=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey("customer_orders.id"), nullable=True)
    route_id = Column(UUID(as_uuid=True), ForeignKey("routes.id"), nullable=True)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=True)
    driver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    status = Column(String(50), default="pending")  # pending, picked, in_transit, delivered, failed
    weight_kg = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)
    scheduled_pickup = Column(DateTime, nullable=True)
    actual_pickup = Column(DateTime, nullable=True)
    scheduled_delivery = Column(DateTime, nullable=True)
    actual_delivery = Column(DateTime, nullable=True)
    delay_risk = Column(Boolean, default=False)
    delay_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ShipmentTracking(Base):
    __tablename__ = "shipment_tracking"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shipment_id = Column(UUID(as_uuid=True), ForeignKey("shipments.id"), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), nullable=True)
    speed_kmh = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)

class DeliverySchedule(Base):
    __tablename__ = "delivery_schedules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    max_stops = Column(Integer, default=20)
    current_stops = Column(Integer, default=0)
    status = Column(String(50), default="open")  # open, full, in_progress, completed
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
