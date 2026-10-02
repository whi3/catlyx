import logging
import httpx
from urllib.parse import urlparse

from config import settings
logger = logging.getLogger(__name__)


async def send_sms(
    phone_number: str,
    message: str,
) -> bool:

    if not phone_number:
        return False

    if not settings.SMS_ENABLED:
        return False

    if not settings.SMS_PROVIDER_URL or not settings.SMS_API_KEY or not settings.SMS_SENDER_ID:
        logger.error("SMS is enabled but provider configuration is incomplete.")
        return False
    if urlparse(settings.SMS_PROVIDER_URL).scheme != "https":
        logger.error("SMS provider URL must use HTTPS.")
        return False

    try:

        headers = {
            "Authorization": (
                f"Bearer {settings.SMS_API_KEY}"
            ),
            "Content-Type": "application/json",
        }

        payload = {
            "to": phone_number,
            "message": message,
            "sender": settings.SMS_SENDER_ID,
        }

        async with httpx.AsyncClient(
            timeout=10
        ) as client:

            response = await client.post(
                settings.SMS_PROVIDER_URL,
                json=payload,
                headers=headers,
            )

        if response.is_success:

            return True

        logger.warning("SMS provider returned HTTP %s.", response.status_code)

        return False

    except httpx.HTTPError:
        logger.exception("SMS provider request failed.")
        return False
