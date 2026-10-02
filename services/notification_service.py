import uuid
import logging
from datetime import datetime, timezone
from fastapi import HTTPException
from core.firebase import db
from config import settings
from schemas.notification import NotificationCreate
from services.sms_service import send_sms

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

    (
        db.collection(COLLECTION)
        .document(notification_id)
        .set(data)
    )

    return data
    
def update_notification_status(notification_id: str, status: str):
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

    try:
        sent = await send_sms(phone_number, message)
        status = "sent" if sent else "failed"
    except Exception:
        logger.exception("Referral SMS delivery failed; notification remains in the outbox.")
        status = "failed"
    try:
        update_notification_status(notification["notification_id"], status)
    except Exception:
        logger.exception("Could not update referral notification delivery status.")
        return "pending"
    return status
