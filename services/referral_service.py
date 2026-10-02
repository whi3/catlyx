import uuid
from datetime import datetime, timezone
from fastapi import HTTPException
from core.firebase import db
from core.access_control import ensure_facility_access
from schemas.referral import ReferralCreate, ReferralStatusUpdate

COLLECTION = "referrals"

def create_referral(referral: ReferralCreate, created_by: str, current_user: dict):
    if db is None:
        raise HTTPException(status_code=503, detail="Database service is not configured.")
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

    patient_data = patient_document.to_dict() or {}
    ensure_facility_access(patient_data, current_user)

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
    data["facility_id"] = patient_data.get("facility_id")

    (
        db.collection(COLLECTION)
        .document(referral_id)
        .set(data)
    )

    return data


def get_referral(referral_id: str, current_user: dict):
    if db is None:
        raise HTTPException(status_code=503, detail="Database service is not configured.")

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

    data = document.to_dict() or {}
    ensure_facility_access(data, current_user)
    return data


def update_referral_status(
    referral_id: str,
    update: ReferralStatusUpdate,
    updated_by: str,
    current_user: dict,
):
    if db is None:
        raise HTTPException(status_code=503, detail="Database service is not configured.")

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

    current_data = document.to_dict() or {}
    ensure_facility_access(current_data, current_user)

    transitions = {
        "pending": {"completed", "cancelled"},
        "completed": set(),
        "cancelled": set(),
    }
    current_status = current_data.get("status", "pending")
    if update.status not in transitions.get(current_status, set()):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status transition from {current_status} to {update.status}.",
        )

    data = {
        "status": update.status,
        "updated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "updated_by": updated_by,
    }
    if update.status == "completed":
        data["completed_at"] = data["updated_at"]
    elif update.status == "cancelled":
        data["cancelled_at"] = data["updated_at"]

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
