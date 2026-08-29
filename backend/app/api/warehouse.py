from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.database import get_db
from app.models.warehouse import WarehouseTask, Inventory, StockMovement
from app.schemas.warehouse import (
    WarehouseTaskCreate, WarehouseTaskResponse, InventoryResponse, AnomalyResponse
)
from app.services.warehouse_service import WarehouseService
from app.utils.security import get_current_user

router = APIRouter()
warehouse_service = WarehouseService()

@router.get("/tasks", response_model=List[WarehouseTaskResponse])
async def get_tasks(
    status: str = Query(None),
    priority: str = Query(None),
    skip: int = Query(0),
    limit: int = Query(10),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get warehouse tasks with filters"""
    query = db.query(WarehouseTask)
    
    if status:
        query = query.filter(WarehouseTask.status == status)
    if priority:
        query = query.filter(WarehouseTask.priority == priority)
    
    tasks = query.offset(skip).limit(limit).all()
    return tasks

@router.post("/tasks", response_model=WarehouseTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: WarehouseTaskCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create new warehouse task"""
    new_task = warehouse_service.create_task(db, task)
    return new_task

@router.get("/tasks/{task_id}", response_model=WarehouseTaskResponse)
async def get_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get specific task"""
    task = db.query(WarehouseTask).filter(WarehouseTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/tasks/{task_id}", response_model=WarehouseTaskResponse)
async def update_task(
    task_id: UUID,
    task_update: WarehouseTaskCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update warehouse task"""
    task = db.query(WarehouseTask).filter(WarehouseTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    updated_task = warehouse_service.update_task(db, task, task_update)
    return updated_task

@router.get("/inventory", response_model=List[InventoryResponse])
async def get_inventory(
    skip: int = Query(0),
    limit: int = Query(10),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get inventory items"""
    items = db.query(Inventory).offset(skip).limit(limit).all()
    return items

@router.get("/anomalies", response_model=List[AnomalyResponse])
async def detect_anomalies(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Detect warehouse anomalies"""
    anomalies = warehouse_service.detect_anomalies(db)
    return anomalies

@router.post("/stock-count/{inventory_id}")
async def perform_stock_count(
    inventory_id: UUID,
    actual_count: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Perform inventory stock count"""
    result = warehouse_service.perform_stock_count(db, inventory_id, actual_count, current_user.id)
    return result
