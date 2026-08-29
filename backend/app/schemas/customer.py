from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class CustomerBase(BaseModel):
    customer_name: str
    email: EmailStr
    phone: str
    address: str
    city: str
    postal_code: str
    country: str

class CustomerCreate(CustomerBase):
    customer_type: str = "business"
    contact_person: Optional[str] = None
    preferred_contact: str = "email"

class CustomerResponse(CustomerBase):
    id: UUID
    customer_type: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class CustomerOrderBase(BaseModel):
    order_number: str
    customer_id: UUID
    total_amount: float
    items: List[Dict[str, Any]]
    delivery_address: str

class CustomerOrderCreate(CustomerOrderBase):
    delivery_date: Optional[datetime] = None
    notes: Optional[str] = None

class CustomerOrderResponse(CustomerOrderBase):
    id: UUID
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MessageTemplateBase(BaseModel):
    template_name: str
    template_type: str
    channel: str
    body: str

class MessageTemplateCreate(MessageTemplateBase):
    subject: Optional[str] = None
    variables: Optional[List[Dict[str, str]]] = None

class MessageTemplateResponse(MessageTemplateBase):
    id: UUID
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class CommunicationBase(BaseModel):
    customer_id: UUID
    communication_type: str
    message_body: str
    recipient: str

class CommunicationCreate(CommunicationBase):
    subject: Optional[str] = None
    order_id: Optional[UUID] = None
    template_id: Optional[UUID] = None

class CommunicationResponse(CommunicationBase):
    id: UUID
    status: str
    is_ai_generated: bool
    sent_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
