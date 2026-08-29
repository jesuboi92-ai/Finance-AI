from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.dialects.postgresql import UUID, JSON
from datetime import datetime
import uuid
from app.database import Base

class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sku = Column(String(100), unique=True, nullable=False, index=True)
    product_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    quantity = Column(Integer, default=0)
    reserved_quantity = Column(Integer, default=0)
    available_quantity = Column(Integer, default=0)
    reorder_level = Column(Integer, default=10)
    unit_price = Column(Float, nullable=False)
    location = Column(String(100), nullable=True)  # Rack/Shelf location
    category = Column(String(100), nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    last_stock_count = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class StockMovement(Base):
    __tablename__ = "stock_movements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inventory_id = Column(UUID(as_uuid=True), ForeignKey("inventory.id"), nullable=False)
    movement_type = Column(String(50), nullable=False)  # inbound, outbound, adjustment, transfer
    quantity = Column(Integer, nullable=False)
    reference_id = Column(String(100), nullable=True)  # Order/Task reference
    notes = Column(Text, nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class WarehouseItem(Base):
    __tablename__ = "warehouse_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inventory_id = Column(UUID(as_uuid=True), ForeignKey("inventory.id"), nullable=False)
    batch_number = Column(String(100), nullable=True)
    serial_number = Column(String(100), unique=True, nullable=True)
    receiving_date = Column(DateTime, nullable=True)
    condition = Column(String(50), default="good")  # good, damaged, expired
    location_zone = Column(String(50), nullable=True)  # A, B, C, D zones
    location_rack = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class WarehouseTask(Base):
    __tablename__ = "warehouse_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_type = Column(String(50), nullable=False)  # picking, packing, receiving, counting, organizing
    status = Column(String(50), default="pending")  # pending, in_progress, completed, cancelled
    priority = Column(String(20), default="medium")  # low, medium, high, urgent
    description = Column(Text, nullable=False)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    inventory_id = Column(UUID(as_uuid=True), ForeignKey("inventory.id"), nullable=True)
    quantity = Column(Integer, nullable=True)
    order_reference = Column(String(100), nullable=True)
    due_date = Column(DateTime, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    anomalies = Column(JSON, nullable=True)  # Store detected anomalies
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
