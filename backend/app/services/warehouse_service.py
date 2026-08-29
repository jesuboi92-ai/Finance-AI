from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.warehouse import WarehouseTask, Inventory, StockMovement
from app.schemas.warehouse import WarehouseTaskCreate
from datetime import datetime
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

class WarehouseService:
    def create_task(self, db: Session, task: WarehouseTaskCreate) -> WarehouseTask:
        """Create new warehouse task"""
        db_task = WarehouseTask(
            task_type=task.task_type,
            description=task.description,
            priority=task.priority,
            due_date=task.due_date,
            assigned_to=task.assigned_to,
            inventory_id=task.inventory_id,
            quantity=task.quantity
        )
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        logger.info(f"Task created: {db_task.id}")
        return db_task
    
    def update_task(self, db: Session, task: WarehouseTask, task_update: WarehouseTaskCreate) -> WarehouseTask:
        """Update warehouse task"""
        task.description = task_update.description
        task.priority = task_update.priority
        task.due_date = task_update.due_date
        task.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(task)
        return task
    
    def detect_anomalies(self, db: Session) -> list:
        """Detect warehouse anomalies like low stock, expired items"""
        anomalies = []
        
        # Check for low stock
        low_stock = db.query(Inventory).filter(
            Inventory.available_quantity <= Inventory.reorder_level
        ).all()
        
        for item in low_stock:
            anomalies.append({
                "type": "low_stock",
                "message": f"Stock level low for {item.product_name}: {item.available_quantity} < {item.reorder_level}",
                "severity": "high",
                "timestamp": datetime.utcnow(),
                "sku": item.sku
            })
        
        # Check for expired items
        expired = db.query(Inventory).filter(
            and_(
                Inventory.expiry_date.isnot(None),
                Inventory.expiry_date <= datetime.utcnow()
            )
        ).all()
        
        for item in expired:
            anomalies.append({
                "type": "expired_item",
                "message": f"Item expired: {item.product_name} (expiry: {item.expiry_date})",
                "severity": "critical",
                "timestamp": datetime.utcnow(),
                "sku": item.sku
            })
        
        # Check for discrepancies in stock counts
        unmatched_counts = db.query(WarehouseTask).filter(
            WarehouseTask.task_type == "counting",
            WarehouseTask.status == "completed",
            WarehouseTask.anomalies.isnot(None)
        ).all()
        
        for task in unmatched_counts:
            if task.anomalies:
                anomalies.append({
                    "type": "stock_discrepancy",
                    "message": f"Stock discrepancy in task {task.id}",
                    "severity": "medium",
                    "timestamp": datetime.utcnow(),
                    "task_id": str(task.id)
                })
        
        return anomalies
    
    def perform_stock_count(self, db: Session, inventory_id: UUID, actual_count: int, user_id: UUID) -> dict:
        """Perform physical stock count and record discrepancies"""
        inventory = db.query(Inventory).filter(Inventory.id == inventory_id).first()
        if not inventory:
            return {"error": "Inventory not found"}
        
        system_count = inventory.quantity
        discrepancy = actual_count - system_count
        
        # Create stock movement record
        if discrepancy != 0:
            movement = StockMovement(
                inventory_id=inventory_id,
                movement_type="adjustment",
                quantity=discrepancy,
                notes=f"Stock count adjustment. System: {system_count}, Actual: {actual_count}",
                created_by=user_id
            )
            db.add(movement)
            
            # Update inventory
            inventory.quantity = actual_count
            inventory.available_quantity = actual_count - inventory.reserved_quantity
            inventory.last_stock_count = datetime.utcnow()
        
        db.commit()
        
        return {
            "inventory_id": str(inventory_id),
            "system_count": system_count,
            "actual_count": actual_count,
            "discrepancy": discrepancy,
            "status": "completed"
        }
