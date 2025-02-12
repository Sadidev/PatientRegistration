from typing import Dict, Any
import logging
from .base import NotificationService

logger = logging.getLogger(__name__)

class SMSService(NotificationService):
    """Placeholder for future SMS implementation"""
    async def send_notification(self, recipient: str, template_name: str, data: Dict[str, Any]) -> None:
        # This will be implemented when SMS provider is chosen
        pass