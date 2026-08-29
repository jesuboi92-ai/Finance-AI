"""SMS service using Twilio"""
from twilio.rest import Client
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class SMSService:
    def __init__(self):
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        else:
            self.client = None
    
    def send_sms(self, phone_number: str, message: str) -> bool:
        """Send SMS via Twilio"""
        if not self.client:
            logger.warning("Twilio credentials not configured")
            return False
        
        try:
            sms = self.client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number
            )
            logger.info(f"SMS sent to {phone_number}: {sms.sid}")
            return True
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            return False
    
    def send_bulk_sms(self, phone_numbers: list, message: str) -> bool:
        """Send bulk SMS messages"""
        if not self.client:
            logger.warning("Twilio credentials not configured")
            return False
        
        try:
            for phone in phone_numbers:
                self.send_sms(phone, message)
            return True
        except Exception as e:
            logger.error(f"Error sending bulk SMS: {e}")
            return False

sms_service = SMSService()
