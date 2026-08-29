"""Utility functions"""
import uuid
from datetime import datetime

def generate_shipment_number() -> str:
    """Generate unique shipment number"""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    unique_id = str(uuid.uuid4())[:8].upper()
    return f"SHIP-{timestamp}-{unique_id}"

def generate_order_number() -> str:
    """Generate unique order number"""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    unique_id = str(uuid.uuid4())[:6].upper()
    return f"ORD-{timestamp}-{unique_id}"

def format_currency(amount: float, currency: str = "EUR") -> str:
    """Format currency for display"""
    return f"{currency} {amount:,.2f}"

def format_phone(phone: str) -> str:
    """Format phone number"""
    # Simple formatting, can be extended
    digits = ''.join(filter(str.isdigit, phone))
    if len(digits) == 10:
        return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
    return phone
