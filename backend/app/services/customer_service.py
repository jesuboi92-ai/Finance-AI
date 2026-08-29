from sqlalchemy.orm import Session
from app.models.customer import Customer, CustomerOrder, Communication, MessageTemplate
from app.models.management import Anomaly
from app.schemas.customer import CustomerCreate, CustomerOrderCreate, CommunicationCreate
from datetime import datetime
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

class CustomerService:
    def create_customer(self, db: Session, customer: CustomerCreate) -> Customer:
        """Create new customer"""
        db_customer = Customer(
            customer_name=customer.customer_name,
            customer_type=customer.customer_type,
            email=customer.email,
            phone=customer.phone,
            address=customer.address,
            city=customer.city,
            postal_code=customer.postal_code,
            country=customer.country,
            contact_person=customer.contact_person,
            preferred_contact=customer.preferred_contact
        )
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)
        logger.info(f"Customer created: {db_customer.id}")
        return db_customer
    
    def create_order(self, db: Session, order: CustomerOrderCreate) -> CustomerOrder:
        """Create customer order"""
        db_order = CustomerOrder(
            order_number=order.order_number,
            customer_id=order.customer_id,
            total_amount=order.total_amount,
            items=order.items,
            delivery_address=order.delivery_address,
            delivery_date=order.delivery_date,
            notes=order.notes
        )
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        logger.info(f"Order created: {db_order.id}")
        return db_order
    
    def generate_communication(self, db: Session, communication: CommunicationCreate) -> Communication:
        """Generate AI communication draft"""
        # In production, use OpenAI/LangChain for AI generation
        template_body = ""
        
        if communication.template_id:
            template = db.query(MessageTemplate).filter(
                MessageTemplate.id == communication.template_id
            ).first()
            if template:
                template_body = template.body
        
        db_communication = Communication(
            customer_id=communication.customer_id,
            order_id=communication.order_id,
            communication_type=communication.communication_type,
            subject=communication.subject,
            message_body=communication.message_body or template_body,
            recipient=communication.recipient,
            template_id=communication.template_id,
            is_ai_generated=True,
            status="draft"
        )
        db.add(db_communication)
        db.commit()
        db.refresh(db_communication)
        logger.info(f"Communication draft created: {db_communication.id}")
        return db_communication
    
    def send_communication(self, db: Session, comm_id: UUID, approved_by: UUID) -> dict:
        """Approve and send communication"""
        communication = db.query(Communication).filter(
            Communication.id == comm_id
        ).first()
        
        if not communication:
            return {"error": "Communication not found"}
        
        # In production, actually send email/SMS
        communication.status = "sent"
        communication.sent_at = datetime.utcnow()
        communication.approved_by = approved_by
        db.commit()
        
        logger.info(f"Communication sent: {comm_id}")
        return {
            "communication_id": str(comm_id),
            "status": "sent",
            "sent_at": communication.sent_at
        }
    
    def notify_delay(self, db: Session, order_id: UUID, reason: str) -> dict:
        """Send delay notification to customer"""
        order = db.query(CustomerOrder).filter(
            CustomerOrder.id == order_id
        ).first()
        
        if not order:
            return {"error": "Order not found"}
        
        customer = db.query(Customer).filter(
            Customer.id == order.customer_id
        ).first()
        
        if not customer:
            return {"error": "Customer not found"}
        
        # Create communication
        notification = Communication(
            customer_id=customer.id,
            order_id=order_id,
            communication_type="notification",
            subject="Delivery Delay Notification",
            message_body=f"We regret to inform you that your order {order.order_number} will be delayed. Reason: {reason}",
            recipient=customer.email,
            status="sent",
            sent_at=datetime.utcnow(),
            is_ai_generated=False
        )
        db.add(notification)
        db.commit()
        
        logger.info(f"Delay notification sent for order {order_id}")
        return {
            "order_id": str(order_id),
            "status": "notified",
            "notification_id": str(notification.id)
        }
