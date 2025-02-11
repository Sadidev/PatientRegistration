import asyncio
import logging

logger = logging.getLogger(__name__)

async def send_confirmation_email(email: str) -> None:
    try:
        # Replace with actual email sending logic
        await asyncio.sleep(1)
        logger.info(f"Confirmation email sent to {email}")
    except Exception as e:
        logger.error(f"Failed to send confirmation email to {email}: {e}")