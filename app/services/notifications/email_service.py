from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
import logging
from jinja2 import Environment, select_autoescape, FileSystemLoader
from typing import Dict, Any

from .base import NotificationService
from app.config import settings

logger = logging.getLogger(__name__)

class EmailService(NotificationService):
    def __init__(self):
        self.conf = ConnectionConfig(
            MAIL_USERNAME=settings.MAIL_USERNAME,
            MAIL_PASSWORD=settings.MAIL_PASSWORD,
            MAIL_FROM=settings.MAIL_FROM,
            MAIL_PORT=settings.MAIL_PORT,
            MAIL_SERVER=settings.MAIL_SERVER,
            MAIL_STARTTLS=settings.MAIL_STARTTLS,
            MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
            TEMPLATE_FOLDER=settings.TEMPLATE_FOLDER,
            USE_CREDENTIALS=True
        )
        self.fast_mail = FastMail(self.conf)

        self.template_env = Environment(
            loader=FileSystemLoader(settings.TEMPLATE_FOLDER),
            autoescape=select_autoescape(['html', 'xml'])
        )

    async def send_notification(self, recipient: str, template_name: str, data: Dict[str, Any]) -> None:
        try:
            template = self.template_env.get_template(f"email/{template_name}.html")
            html_content = template.render(**data)

            message = MessageSchema(
                subject=data.get('subject', 'Notification'),
                recipients=[recipient],
                body=html_content,
                subtype="html"
            )

            await self.fast_mail.send_message(message)
            logger.info(f"Email sent to {recipient}")
            
        except Exception as e:
            logger.error(f"Failed to send email to {recipient}: {e}")
            raise

# Create a singleton instance
email_instance = EmailService()