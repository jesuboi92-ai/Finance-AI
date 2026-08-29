from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class InventoryBase(BaseModel):
    sku: str
    product_name: str
    quantity: int
    reorder_level: int
    unit_price: float

class InventoryCreate(InventoryBase):
    description: Optional[str] = None
    category: Optional[str] = None
    location: Optional[str] = None

class InventoryResponse(InventoryBase):
    id: UUID
    reserved_quantity: int
    available_quantity: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class WarehouseTaskBase(BaseModel):
    task_type: str
    description: str
    priority: str = "medium"
    due_date: datetime

class WarehouseTaskCreate(WarehouseTaskBase):
    assigned_to: Optional[UUID] = None
    inventory_id: Optional[UUID] = None
    quantity: Optional[int] = None

class WarehouseTaskResponse(WarehouseTaskBase):
    id: UUID
    status: str
    assigned_to: Optional[UUID]
    inventory_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AnomalyResponse(BaseModel):
    type: str
    message: str
    severity: str
    timestamp: datetime
