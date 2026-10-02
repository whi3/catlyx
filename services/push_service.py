"""Firebase Cloud Messaging delivery adapter."""

import logging

import firebase_admin
from firebase_admin import messaging
from core.firebase import db

logger = logging.getLogger(__name__)


def send_push(device_token: str, title: str, body: str, data: dict | None = None) -> bool:
    if not firebase_admin._apps:
        logger.error("Push delivery requested before Firebase was initialized.")
        return False

    payload = {
        str(key): str(value)
        for key, value in (data or {}).items()
        if value is not None
    }
    try:
        messaging.send(
            messaging.Message(
                token=device_token,
                notification=messaging.Notification(title=title, body=body),
                data=payload,
            )
        )
        return True
    except Exception:
        # Never log a device token or message body; both may be sensitive.
        logger.exception("Firebase push delivery failed.")
        return False


def register_device_token(user_id: str, token: str) -> None:
    if db is None:
        raise RuntimeError("Firebase is not configured.")
    user_ref = db.collection("users").document(user_id)
    user = user_ref.get()
    if not user.exists:
        raise ValueError("User account is not provisioned.")
    user_ref.update({"device_tokens": firestore_array_union(token)})


def firestore_array_union(token: str):
    # Keep firebase_admin's Firestore helper lazy so pure schema tests do not
    # need an active Firebase application.
    from firebase_admin import firestore

    return firestore.ArrayUnion([token])


async def notify_facility_supervisors_of_referral(
    *, facility_id: str, patient_id: str, referral_id: str, destination: str
) -> int:
    if db is None:
        return 0
    try:
        supervisors = (
            db.collection("users")
            .where("facility_id", "==", facility_id)
            .where("role", "==", "SUPERVISOR")
            .stream()
        )
        from services.notification_service import dispatch_push_notification

        sent = 0
        for snapshot in supervisors:
            profile = snapshot.to_dict() or {}
            for token in profile.get("device_tokens", []):
                result = await dispatch_push_notification(
                    patient_id=patient_id,
                    referral_id=referral_id,
                    device_token=token,
                    title="New referral",
                    message=f"A referral was created for {destination}.",
                )
                sent += result == "sent"
        return sent
    except Exception:
        logger.exception("Could not dispatch facility referral push notifications.")
        return 0
