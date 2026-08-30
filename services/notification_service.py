import uuid
from datetime import datetime, timezone
from core.firebase import db
from schemas.notification import NotificationCreate

COLLECTION = "notifications"

def create_notification(notification: NotificationCreate,):
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
    
def update_notification_status(notification_id: str,status: str,):
    data = {
        "status": status,
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