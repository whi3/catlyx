import uuid
import logging
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException
from core.firebase import db
from config import settings
from schemas.notification import NotificationCreate
from services.sms_service import send_sms
from services.push_service import send_push

COLLECTION = "notifications"
logger = logging.getLogger(__name__)

def create_notification(notification: NotificationCreate,):
    if db is None:
        raise HTTPException(status_code=503, detail="Database service is not configured.")
    notification_id = str(uuid.uuid4())
    created_at = datetime.now(
        timezone.utc
    ).isoformat()

    data = notification.model_dump()
    data["notification_id"] = notification_id
    data["status"] = "pending"
    data["created_at"] = created_at
    data["sent_at"] = None
    data["attempt_count"] = 0
    data["max_attempts"] = max(1, settings.NOTIFICATION_MAX_ATTEMPTS)
    data["next_attempt_at"] = created_at

    (
        db.collection(COLLECTION)
        .document(notification_id)
        .set(data)
    )

    return data
    
def update_notification_status(
    notification_id: str,
    status: str,
    *,
    attempt_count: int | None = None,
    next_attempt_at: str | None = None,
    last_error: str | None = None,
):
    if db is None:
        raise HTTPException(status_code=503, detail="Database service is not configured.")
    if status not in {"pending", "sent", "failed"}:
        raise HTTPException(status_code=422, detail="Invalid notification status.")
    document = db.collection(COLLECTION).document(notification_id).get()
    if not document.exists:
        raise HTTPException(status_code=404, detail="Notification not found.")
    data = {
        "status": status,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    if attempt_count is not None:
        data["attempt_count"] = attempt_count
    data["next_attempt_at"] = next_attempt_at
    data["last_error"] = last_error[:300] if last_error else None

    if status == "sent":
        data["sent_at"] = datetime.now(
            timezone.utc
        ).isoformat()

    (
        db.collection(COLLECTION)
        .document(notification_id)
        .update(data)
    )

    return {
        "notification_id": notification_id,
        "status": status,
    }


async def dispatch_referral_sms(
    *, patient_id: str, referral_id: str, phone_number: str, message: str
) -> str:
    """Persist an outbox record before delivery; provider failures never undo referrals."""
    try:
        notification = create_notification(
            NotificationCreate(
                patient_id=patient_id,
                referral_id=referral_id,
                phone_number=phone_number,
                message=message,
            )
        )
    except Exception:
        logger.exception("Could not persist referral notification.")
        return "failed"
    if not settings.SMS_ENABLED:
        return "pending"

    return await _deliver_notification(notification)


async def dispatch_push_notification(
    *,
    patient_id: str,
    referral_id: str,
    device_token: str,
    title: str,
    message: str,
) -> str:
    notification = create_notification(NotificationCreate(
        patient_id=patient_id,
        referral_id=referral_id,
        channel="push",
        device_token=device_token,
        title=title,
        message=message,
    ))
    return await _deliver_notification(notification)


async def _deliver_notification(notification: dict) -> str:
    """Attempt delivery and schedule bounded exponential retries in the outbox."""
    channel = notification.get("channel", "sms")
    if channel == "sms" and not settings.SMS_ENABLED:
        return "pending"
    try:
        if channel == "sms":
            sent = await send_sms(notification["phone_number"], notification["message"])
        elif channel == "push":
            sent = send_push(
                notification["device_token"],
                notification.get("title") or "CatalystCare",
                notification["message"],
                {"referral_id": notification["referral_id"]},
            )
        else:
            logger.error("Unsupported notification channel %r.", channel)
            sent = False
    except Exception:
        logger.exception("Notification provider call failed for channel %r.", channel)
        sent = False

    attempt_count = int(notification.get("attempt_count", 0)) + 1
    max_attempts = max(1, int(notification.get("max_attempts", settings.NOTIFICATION_MAX_ATTEMPTS)))
    if sent:
        status = "sent"
        next_attempt_at = None
    elif attempt_count >= max_attempts:
        status = "failed"
        next_attempt_at = None
    else:
        status = "pending"
        delay_minutes = min(60, 2 ** attempt_count)
        next_attempt_at = (
            datetime.now(timezone.utc) + timedelta(minutes=delay_minutes)
        ).isoformat()
    try:
        update_notification_status(
            notification["notification_id"],
            status,
            attempt_count=attempt_count,
            next_attempt_at=next_attempt_at,
            last_error=None if sent else "Provider delivery failed.",
        )
    except Exception:
        logger.exception("Could not update notification delivery status.")
        return "pending"
    return status


async def retry_due_notifications(limit: int = 50) -> dict:
    """Process due outbox entries; run as a single scheduled worker instance."""
    if db is None:
        raise HTTPException(status_code=503, detail="Database service is not configured.")
    if not 1 <= limit <= 100:
        raise HTTPException(status_code=422, detail="Retry limit must be between 1 and 100.")
    now = datetime.now(timezone.utc).isoformat()
    query = (
        db.collection(COLLECTION)
        .where("status", "==", "pending")
        .where("next_attempt_at", "<=", now)
        .limit(limit)
    )
    processed = sent = failed = 0
    for document in query.stream():
        notification = document.to_dict() or {}
        notification.setdefault("notification_id", document.id)
        try:
            result = await _deliver_notification(notification)
        except Exception:
            logger.exception("Notification worker failed for outbox item %s.", document.id)
            result = "failed"
        processed += 1
        sent += result == "sent"
        failed += result == "failed"
    return {"processed": processed, "sent": sent, "failed": failed}
