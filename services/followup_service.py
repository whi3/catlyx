import uuid
import logging
from datetime import datetime, timezone
from fastapi import HTTPException
from core.access_control import ensure_facility_access, facility_query
from core.firebase import db
from schemas.followup import FollowUpCreate, FollowUpOutcome
from schemas.referral import ReferralFollowUpCreate


COLLECTION = "followups"
logger = logging.getLogger(__name__)

def _get_followup(followup_id: str):
    if db is None:
        raise HTTPException(status_code=503, detail="Database service is not configured.")
    document = db.collection(COLLECTION).document(followup_id).get()

    if not document.exists:
        raise HTTPException(status_code=404, detail="Follow-up not found")
    
    return document.to_dict()

def schedule_followup(followup: FollowUpCreate, created_by: str, current_user: dict):
    if db is None:
        raise HTTPException(status_code=503, detail="Database service is not configured.")
    referral = (db.collection("referrals").document(followup.referral_id).get())

    if not referral.exists:
        raise HTTPException(status_code=404, detail="Referral not found")

    referral_data = referral.to_dict()
    ensure_facility_access(referral_data, current_user)
    if referral_data.get("patient_id") != followup.patient_id:
        raise HTTPException(
            status_code=422,
            detail="Follow-up patient does not match the referral patient.",
        )
    if referral_data.get("status") != "pending":
        raise HTTPException(status_code=409, detail="Follow-ups can only be scheduled for pending referrals.")

    followup_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc)

    data = {
        "followup_id": followup_id,
        "referral_id": followup.referral_id,
        "patient_id":followup.patient_id,
        "scheduled_date":followup.scheduled_date.astimezone(timezone.utc).isoformat(),
        "status":"pending",
        "outcome":None,
        "notes":followup.notes,
        "completed_at":None,
        "created_at":created_at.isoformat(),
        "created_by":created_by,
        "facility_id":referral_data.get("facility_id"),
    }

    db.collection(COLLECTION).document(followup_id).set(data)

    return data


def record_legacy_referral_followup(
    referral_id: str,
    followup: ReferralFollowUpCreate,
    recorded_by: str,
    current_user: dict,
) -> dict:
    """Keep the old referral close-out endpoint on the canonical followups collection."""
    if db is None:
        raise HTTPException(status_code=503, detail="Database service is not configured.")
    referral = db.collection("referrals").document(referral_id).get()
    if not referral.exists:
        raise HTTPException(status_code=404, detail="Referral not found.")
    referral_data = referral.to_dict() or {}
    ensure_facility_access(referral_data, current_user)

    recorded_at = datetime.now(timezone.utc).isoformat()
    followup_id = str(uuid.uuid4())
    status = "completed" if followup.completed else "pending"
    data = {
        "followup_id": followup_id,
        "referral_id": referral_id,
        "patient_id": referral_data.get("patient_id"),
        "scheduled_date": recorded_at,
        "status": status,
        "outcome": "Recorded through legacy referral follow-up endpoint",
        "notes": followup.notes,
        "completed_at": recorded_at if followup.completed else None,
        "created_at": recorded_at,
        "created_by": recorded_by,
        "facility_id": referral_data.get("facility_id"),
        "legacy_endpoint": True,
    }
    db.collection(COLLECTION).document(followup_id).set(data)
    return {
        "referral_id": referral_id,
        "followup_id": followup_id,
        "message": "Follow-up recorded successfully.",
        "follow_up_required": True,
        "follow_up_completed": followup.completed,
        "follow_up_notes": followup.notes,
        "follow_up_date": recorded_at,
    }


def get_pending_followups(current_user: dict):
    if db is None:
        raise HTTPException(status_code=503, detail="Database service is not configured.")
    documents = facility_query(db.collection(COLLECTION), current_user).stream()

    return [
        document.to_dict()
        for document in documents
        if document.to_dict().get("status") == "pending"
        and (
            current_user.get("role") == "ADMIN"
            or document.to_dict().get("facility_id") == current_user.get("facility_id")
        )
    ]

def get_overdue_followups(current_user: dict):
    now = datetime.now(timezone.utc)
    followups = get_pending_followups(current_user)
    overdue = []

    for followup in followups:
        try:
            scheduled_date = datetime.fromisoformat(
                followup["scheduled_date"].replace("Z", "+00:00")
            )
            if scheduled_date.tzinfo is None:
                logger.error("Stored follow-up has a timezone-naive scheduled_date.")
                continue
        except (KeyError, TypeError, ValueError):
            logger.error("Stored follow-up has an invalid scheduled_date.")
            continue

        if scheduled_date < now:
            overdue.append(followup)

    return overdue


def record_followup_outcome(
    followup_id: str,
    outcome: FollowUpOutcome,
    updated_by: str,
    current_user: dict,
):
    existing = _get_followup(followup_id)
    ensure_facility_access(existing, current_user)
    if existing.get("status") != "pending":
        raise HTTPException(status_code=409, detail="Only pending follow-ups can be closed.")
    completed_at = None

    if outcome.status == "completed":
        completed_at = datetime.now(timezone.utc).isoformat()

    update_data = {
        "status": outcome.status,
        "outcome": outcome.outcome,
        "notes": outcome.notes,
        "completed_at": completed_at,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "updated_by": updated_by,
    }

    db.collection(COLLECTION).document(followup_id).update(update_data)

    return {
        "followup_id": followup_id,
        "message":"Follow-up outcome recorded successfully.",
        **update_data,
    }
