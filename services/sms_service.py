import httpx

from config import settings


async def send_sms(
    phone_number: str,
    message: str,
) -> bool:

    if not phone_number:
        return False

    if not settings.SMS_ENABLED:
        print(
            f"[SMS DISABLED] "
            f"{phone_number}: {message}"
        )

        return False

    if not settings.SMS_PROVIDER_URL:
        print(
            "[SMS ERROR] "
            "SMS provider URL is not configured."
        )

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

        print(
            "[SMS ERROR] "
            f"Provider returned {response.status_code}"
        )

        return False

    except httpx.HTTPError as error:

        print(
            f"[SMS ERROR] {error}"
        )

        return False