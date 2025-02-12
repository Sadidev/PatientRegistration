from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
import logging
from jinja2 import Environment, select_autoescape, FileSystemLoader

from app.config import settings

logger = logging.getLogger(__name__)

class EmailService:
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

    async def send_patient_confirmation(self, email: EmailStr, patient_name: str) -> None:
        try:
            # Get the template
            template = self.template_env.get_template("confirmation.html")
            
            # Render the template with context
            html_content = template.render(
                patient_name=patient_name,
                confirmation_link=f"https://yourapp.com/confirm?email={email}"
            )

            message = MessageSchema(
                subject="Welcome to Our Medical Practice",
                recipients=[email],
                body=html_content,
                subtype="html"
            )

            await self.fast_mail.send_message(message)
            logger.info(f"Confirmation email sent to {email}")
            
        except Exception as e:
            logger.error(f"Failed to send confirmation email to {email}: {e}")
            raise

# Create a singleton instance
email_instance = EmailService()