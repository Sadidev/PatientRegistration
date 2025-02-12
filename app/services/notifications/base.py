from abc import ABC, abstractmethod
from typing import Any, Dict

class NotificationService(ABC):
    @abstractmethod
    async def send_notification(self, recipient: str, template_name: str, data: Dict[str, Any]) -> None:
        """Base method for sending any type of notification"""
        pass
