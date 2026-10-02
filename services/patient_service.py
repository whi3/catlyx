import uuid
from datetime import datetime, timezone

from fastapi import HTTPException

from core.firebase import db
from core.access_control import ensure_facility_access, facility_query
from schemas.mother import MotherCreate
from schemas.child import ChildCreate


COLLECTION = "patients"


def register_mother(
    mother: MotherCreate,
    created_by: str,
    facility_id: str,
):
    if db is None:
        raise HTTPException(status_code=503, detail="Database service is not configured.")
    if not facility_id:
        raise HTTPException(status_code=403, detail="User account has no facility assignment.")
    patient_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    data = mother.model_dump(mode="json")

    data["patient_id"] = patient_id
    data["patient_type"] = "mother"

    data["created_at"] = now
    data["updated_at"] = now
    data["created_by"] = created_by
    data["facility_id"] = facility_id

    db.collection(COLLECTION).document(patient_id).set(data)

    return {
        "patient_id": patient_id,
        "message": "Mother registered successfully.",
    }


def register_child(child: ChildCreate, created_by: str, facility_id: str):
    if db is None:
        raise HTTPException(status_code=503, detail="Database service is not configured.")
    if not facility_id:
        raise HTTPException(status_code=403, detail="User account has no facility assignment.")
    patient_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    data = child.model_dump()
    data["patient_id"] = patient_id
    data["patient_type"] = "child"

    data["created_at"] = now
    data["updated_at"] = now
    data["created_by"] = created_by
    data["facility_id"] = facility_id

    db.collection(COLLECTION).document(patient_id).set(data)

    return {
        "patient_id": patient_id,
        "message": "Child registered successfully.",
    }


def get_patient(patient_id: str, current_user: dict | None = None):
    if db is None:
        raise HTTPException(status_code=503, detail="Database service is not configured.")
    document = (db.collection(COLLECTION).document(patient_id).get())
    if not document.exists:
        raise HTTPException(
            status_code=404,
            detail="Patient not found.",
        )

    data = document.to_dict()
    if current_user is not None:
        ensure_facility_access(data, current_user)
    return data


def get_all_patients(current_user: dict):
    if db is None:
        raise HTTPException(status_code=503, detail="Database service is not configured.")
    documents = facility_query(db.collection(COLLECTION), current_user).stream()
    patients = []
    
    for document in documents:
        data = document.to_dict()
        if current_user.get("role") == "ADMIN" or data.get("facility_id") == current_user.get("facility_id"):
            patients.append(data)

    return patients
    
def get_patient_phone_number(patient_id: str,):
    if db is None:
        raise HTTPException(status_code=503, detail="Database service is not configured.")
    document = (
        db.collection(COLLECTION)
        .document(patient_id)
        .get()
    )

    if not document.exists:
        return None

    data = document.to_dict()

    return data.get("phone_number")
