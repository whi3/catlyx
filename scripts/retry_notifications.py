"""Process one bounded pass through due notification outbox items.

Schedule this command at a short interval with a single active worker instance.
"""

import asyncio
import logging

from services.notification_service import retry_due_notifications


async def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    result = await retry_due_notifications()
    logging.info("Notification retry pass: %s", result)
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
