from enum import Enum
from typing import Dict, Any
from .email_service import EmailService
from .sms_service import SMSService

class NotificationType(Enum):
    EMAIL = "email"
    SMS = "sms"

class NotificationManager:
    def __init__(self):
        self.services = {
            NotificationType.EMAIL: EmailService(),
            NotificationType.SMS: SMSService()
        }

    async def send_patient_confirmation(
        self,
        notification_type: NotificationType,
        recipient: str,
        patient_name: str
    ) -> None:
        service = self.services[notification_type]
        data = {
            "subject": "Welcome to Our Medical Practice",
            "patient_name": patient_name,
            "confirmation_link": f"https://yourapp.com/confirm?email={recipient}"
        }
        await service.send_notification(recipient, "confirmation", data)