from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.database import get_db
from app.models.customer import Customer, CustomerOrder, Communication, MessageTemplate
from app.schemas.customer import (
    CustomerCreate, CustomerResponse, CustomerOrderCreate, CustomerOrderResponse,
    CommunicationCreate, CommunicationResponse, MessageTemplateResponse
)
from app.services.customer_service import CustomerService
from app.utils.security import get_current_user

router = APIRouter()
customer_service = CustomerService()

@router.get("/customers", response_model=List[CustomerResponse])
async def get_customers(
    skip: int = Query(0),
    limit: int = Query(10),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all customers"""
    customers = db.query(Customer).filter(Customer.is_active == True).offset(skip).limit(limit).all()
    return customers

@router.post("/customers", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create new customer"""
    new_customer = customer_service.create_customer(db, customer)
    return new_customer

@router.get("/orders", response_model=List[CustomerOrderResponse])
async def get_orders(
    status: str = Query(None),
    skip: int = Query(0),
    limit: int = Query(10),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get customer orders"""
    query = db.query(CustomerOrder)
    if status:
        query = query.filter(CustomerOrder.status == status)
    orders = query.offset(skip).limit(limit).all()
    return orders

@router.post("/orders", response_model=CustomerOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order: CustomerOrderCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create customer order"""
    new_order = customer_service.create_order(db, order)
    return new_order

@router.get("/communications", response_model=List[CommunicationResponse])
async def get_communications(
    status: str = Query(None),
    skip: int = Query(0),
    limit: int = Query(10),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get customer communications"""
    query = db.query(Communication)
    if status:
        query = query.filter(Communication.status == status)
    comms = query.offset(skip).limit(limit).all()
    return comms

@router.post("/communications/draft", response_model=CommunicationResponse)
async def draft_communication(
    communication: CommunicationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Draft AI-generated communication"""
    draft = customer_service.generate_communication(db, communication)
    return draft

@router.post("/communications/{comm_id}/approve-and-send")
async def approve_and_send(
    comm_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Approve and send communication"""
    result = customer_service.send_communication(db, comm_id, current_user.id)
    return result

@router.get("/templates", response_model=List[MessageTemplateResponse])
async def get_templates(
    template_type: str = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get message templates"""
    query = db.query(MessageTemplate).filter(MessageTemplate.is_active == True)
    if template_type:
        query = query.filter(MessageTemplate.template_type == template_type)
    templates = query.all()
    return templates

@router.post("/notifications/delay/{order_id}")
async def notify_delay(
    order_id: UUID,
    reason: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Send delay notification to customer"""
    result = customer_service.notify_delay(db, order_id, reason)
    return result
