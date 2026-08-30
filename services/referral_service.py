import uuid
from datetime import datetime, timezone
from fastapi import HTTPException
from core.firebase import db
from schemas.referral import (
    ReferralCreate,
    ReferralStatusUpdate,
    FollowUpCreate,
)

COLLECTION = "referrals"

def create_referral(referral: ReferralCreate, created_by: str,):
    patient_document = (
        db.collection("patients")
        .document(referral.patient_id)
        .get()
    )

    if not patient_document.exists:
        raise HTTPException(
            status_code=404,
            detail="Patient not found."
        )

    referral_id = str(uuid.uuid4())

    created_at = (
        datetime.now(timezone.utc)
        .isoformat()
    )

    data = referral.model_dump()

    data["referral_id"] = referral_id
    data["status"] = "pending"
    
    data["created_at"] = created_at
    data["updated_at"] = created_at
    data["created_by"] = created_by

    data["follow_up_required"] = False
    data["follow_up_completed"] = False
    data["follow_up_notes"] = None
    data["follow_up_date"] = None

    (
        db.collection(COLLECTION)
        .document(referral_id)
        .set(data)
    )

    return data


def get_referral(referral_id: str):

    document = (
        db.collection(COLLECTION)
        .document(referral_id)
        .get()
    )

    if not document.exists:
        raise HTTPException(
            status_code=404,
            detail="Referral not found."
        )

    return document.to_dict()


def update_referral_status(
    referral_id: str,
    update: ReferralStatusUpdate,
    updated_by: str,
):

    document = (
        db.collection(COLLECTION)
        .document(referral_id)
        .get()
    )

    if not document.exists:
        raise HTTPException(
            status_code=404,
            detail="Referral not found."
        )

    allowed_statuses = {
        "pending",
        "completed",
        "cancelled",
    }

    if update.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid referral status. "
                "Use pending, completed, or cancelled."
            )
        )

    data = {
        "status": update.status,
        "updated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "updated_by": updated_by,
    }

    (
        db.collection(COLLECTION)
        .document(referral_id)
        .update(data)
    )

    return {
        "referral_id": referral_id,
        "status": update.status,
        "message": "Referral status updated successfully."
    }

def record_follow_up(referral_id: str,follow_up: FollowUpCreate,recorded_by: str,):
    document = (
        db.collection(COLLECTION)
        .document(referral_id)
        .get()
    )

    if not document.exists:
        raise HTTPException(
            status_code=404,
            detail="Referral not found."
        )

    follow_up_date = (
        datetime.now(timezone.utc)
        .isoformat()
    )

    data = {
        "follow_up_required": True,
        "follow_up_completed": follow_up.completed,
        "follow_up_notes": follow_up.notes,
        "follow_up_date": follow_up_date,
        "follow_up_recorded_by": recorded_by,
        "updated_at": follow_up_date,
    }
    
    (
        db.collection(COLLECTION)
        .document(referral_id)
        .update(data)
    )

    return {
        "referral_id": referral_id,
        "message": "Follow-up recorded successfully.",
        **data,
    }