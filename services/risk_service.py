import uuid
from datetime import datetime, timezone
from fastapi import HTTPException
from pydantic import ValidationError
from core.firebase import db
from core.access_control import ensure_facility_access
from config import settings
from schemas.risk import (RiskAssessmentResponse,)
from schemas.mother_risk import (MotherRiskAssessmentRequest,)
from schemas.child_risk import (ChildRiskAssessmentRequest,)
from ai.mother_engine import (assess_mother_risk,)
from ai.child_engine import (assess_child_risk,)


COLLECTION = "risk_assessments"


def get_patient(patient_id: str, current_user: dict | None = None):
    if db is None:
        raise HTTPException(status_code=503, detail="Database service is not configured.")
    document = (
        db.collection("patients")
        .document(patient_id)
        .get()
    )

    if not document.exists:
        return None

    patient = document.to_dict() or {}
    if current_user is not None:
        ensure_facility_access(patient, current_user)
    return patient


def create_risk_assessment(
    data: dict,
    assessed_by: str,
    current_user: dict,
) -> RiskAssessmentResponse:

    if not settings.RISK_RULES_CLINICALLY_APPROVED:
        raise HTTPException(
            status_code=503,
            detail="Risk decision support is disabled pending clinical approval.",
        )

    patient_id = data.get("patient_id")

    if not patient_id:

        raise HTTPException(
            status_code=422,
            detail="patient_id is required.",
        )

    patient = get_patient(patient_id, current_user=current_user)

    if not patient:

        raise HTTPException(
            status_code=404,
            detail="Patient not found.",
        )

    patient_type = patient.get(
        "patient_type"
    )

    if patient_type == "mother":

        try:

            maternal_fields = {
                "patient_id",
                "pregnancy_weeks",
                "severe_bleeding",
                "convulsions",
                "severe_headache",
                "blurred_vision",
                "swelling",
                "severe_abdominal_pain",
                "fever",
                "difficulty_breathing",
                "reduced_fetal_movement",
                "missed_anc",
            }
            maternal_data = {
                key: value for key, value in data.items() if key in maternal_fields
            }
            screening_fields = maternal_fields - {"patient_id", "pregnancy_weeks"}
            if not screening_fields.intersection(maternal_data):
                raise HTTPException(
                    status_code=422,
                    detail="At least one maternal screening observation is required.",
                )
            if maternal_data.get("pregnancy_weeks") is None:
                maternal_data["pregnancy_weeks"] = patient.get("pregnancy_weeks")
            assessment_data = MotherRiskAssessmentRequest(**maternal_data)

        except ValidationError:

            raise HTTPException(
                status_code=422,
                detail=(
                    "Invalid maternal "
                    "assessment data."
                ),
            )

        result = assess_mother_risk(
            assessment_data
        )

    elif patient_type == "child":
        try:
            child_fields = {
                "patient_id",
                "temperature",
                "difficulty_breathing",
                "severe_diarrhoea",
                "persistent_vomiting",
                "feeding_difficulty",
                "lethargy",
                "convulsions",
                "severe_wasting",
                "missed_immunization",
            }
            child_data = {key: value for key, value in data.items() if key in child_fields}
            screening_fields = child_fields - {"patient_id"}
            if not screening_fields.intersection(child_data):
                raise HTTPException(
                    status_code=422,
                    detail="At least one child screening observation is required.",
                )
            child_data["age_months"] = patient.get("age_months")
            assessment_data = ChildRiskAssessmentRequest(**child_data)

        except ValidationError:

            raise HTTPException(
                status_code=422,
                detail=(
                    "Invalid child "
                    "assessment data."
                ),
            )

        result = assess_child_risk(
            assessment_data
        )

    else:

        raise HTTPException(
            status_code=400,
            detail="Unknown patient type.",
        )

    assessment_id = str(
        uuid.uuid4()
    )

    assessed_at = datetime.now(
        timezone.utc
    ).isoformat()

    assessment_record = {
        "assessment_id": assessment_id,
        "patient_id": patient_id,
        "patient_type": patient_type,
        "risk_level": result.risk_level,
        "risk_score": result.risk_score,
        "reasons": result.reasons,
        "recommendation": result.recommendation,
        "assessed_by": assessed_by,
        "assessed_at": assessed_at,
        "facility_id": patient.get("facility_id"),
        "observations": data,
        "engine_version": "rules-v1",
        "clinical_validation_status": "pending",
        "decision_support_only": True,
    }

    (
        db.collection(COLLECTION)
        .document(assessment_id)
        .set(assessment_record)
    )

    return RiskAssessmentResponse(
        **assessment_record
    )


def get_assessment_history(
    patient_id: str,
    *,
    limit: int = 50,
    cursor: str | None = None,
) -> tuple[list[dict], str | None]:
    if db is None:
        raise HTTPException(status_code=503, detail="Database service is not configured.")
    if not 1 <= limit <= 100:
        raise HTTPException(status_code=422, detail="History limit must be between 1 and 100.")

    collection = db.collection(COLLECTION)
    query = (
        collection
        .where("patient_id", "==", patient_id)
        .order_by("assessed_at", direction="DESCENDING")
        .limit(limit + 1)
    )
    if cursor:
        cursor_document = collection.document(cursor).get()
        cursor_data = cursor_document.to_dict() if cursor_document.exists else None
        if not cursor_data or cursor_data.get("patient_id") != patient_id:
            raise HTTPException(status_code=400, detail="Invalid assessment history cursor.")
        query = query.start_after(cursor_document)

    documents = list(query.stream())
    has_more = len(documents) > limit
    page = documents[:limit]
    assessments = [document.to_dict() for document in page]
    next_cursor = page[-1].id if has_more else None
    return assessments, next_cursor


def get_current_risk(patient_id: str) -> dict:
    history, _ = get_assessment_history(patient_id, limit=1)
    if not history:
        raise HTTPException(status_code=404, detail="No risk assessment found.")
    return history[0]
