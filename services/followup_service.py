import uuid
from datetime import datetime, timezone
from fastapi import HTTPException
from core.firebase import db
from schemas.followup import FollowUpCreate, FollowUpOutcome, FollowUpResponse


COLLECTION = "followups"

def _get_followup(followup_id: str):
    document = db.collection(COLLECTION).document(followup_id).get()

    if not document.exists:
        raise HTTPException(status_code=404, detail="Follow-up not found")
    
    return document.to_dict()

def schedule_followup(followup: FollowUpCreate, created_by: str):
    referral = (db.collection("referrals").document(followup.referral_id).get())

    if not referral.exists:
        raise HTTPException(status_code=404, detail="Referral not found")

    followup_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc)

    data = {
        "followup_id": followup_id,
        "referral_id": followup.referral_id,
        "patient_id":followup.patient_id,
        "scheduled_date":followup.scheduled_date.isoformat(),
        "status":"pending",
        "outcome":None,
        "notes":followup.notes,
        "completed_at":None,
        "created_at":created_at.isoformat(),
        "created_by":created_by,
    }

    db.collection(COLLECTION).document(followup_id).set(data)

    return data


def get_pending_followups():
    documents = db.collection(COLLECTION).stream()

    return [
        document.to_dict()
        for document in documents
        if document.to_dict().get("status") == "pending"
    ]

def get_overdue_followups():
    now = datetime.now(timezone.utc)
    followups = get_pending_followups()
    overdue = []

    for followup in followups:
        scheduled_date = datetime.fromisoformat(
            followup["scheduled_date"]
        )

        if scheduled_date < now:
            overdue.append(followup)

    return overdue


def record_followup_outcome(followup_id: str, outcome: FollowUpOutcome, updated_by: str):
    _get_followup(followup_id)
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