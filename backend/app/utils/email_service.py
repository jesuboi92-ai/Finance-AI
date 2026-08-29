"""Email service using SendGrid"""
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        if settings.SENDGRID_API_KEY:
            self.sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        else:
            self.sg = None
    
    def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send email via SendGrid"""
        if not self.sg:
            logger.warning("SendGrid API key not configured")
            return False
        
        try:
            message = Mail(
                from_email=settings.SENDGRID_FROM_EMAIL,
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )
            self.sg.send(message)
            logger.info(f"Email sent to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def send_bulk_email(self, to_emails: list, subject: str, html_content: str) -> bool:
        """Send bulk emails"""
        if not self.sg:
            logger.warning("SendGrid API key not configured")
            return False
        
        try:
            for email in to_emails:
                self.send_email(email, subject, html_content)
            return True
        except Exception as e:
            logger.error(f"Error sending bulk emails: {e}")
            return False

email_service = EmailService()
