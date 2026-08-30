import uuid
from datetime import datetime, timezone

from fastapi import HTTPException

from core.firebase import db
from schemas.mother import MotherCreate
from schemas.child import ChildCreate


COLLECTION = "patients"


def register_mother(
    mother: MotherCreate,
    created_by: str = "unknown",
):
    patient_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    data = mother.model_dump()

    data["patient_id"] = patient_id
    data["patient_type"] = "mother"

    data["created_at"] = now
    data["updated_at"] = now
    data["created_by"] = created_by

    db.collection(COLLECTION).document(patient_id).set(data)

    return {
        "patient_id": patient_id,
        "message": "Mother registered successfully.",
    }


def register_child(child: ChildCreate,created_by: str = "unknown",):
    patient_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    data = child.model_dump()
    data["patient_id"] = patient_id
    data["patient_type"] = "child"

    data["created_at"] = now
    data["updated_at"] = now
    data["created_by"] = created_by

    db.collection(COLLECTION).document(patient_id).set(data)

    return {
        "patient_id": patient_id,
        "message": "Child registered successfully.",
    }


def get_patient(patient_id: str):
    document = (db.collection(COLLECTION).document(patient_id).get())
    if not document.exists:
        raise HTTPException(
            status_code=404,
            detail="Patient not found.",
        )

    return document.to_dict()


def get_all_patients():
    documents = db.collection(COLLECTION).stream()
    patients = []
    
    for document in documents:
        patients.append(document.to_dict())

    return patients
    
def get_patient_phone_number(patient_id: str,):
    document = (
        db.collection(COLLECTION)
        .document(patient_id)
        .get()
    )

    if not document.exists:
        return None

    data = document.to_dict()

    return data.get("phone_number")