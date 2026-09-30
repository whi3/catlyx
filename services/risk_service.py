import uuid
from datetime import datetime, timezone
from fastapi import HTTPException
from pydantic import ValidationError
from core.firebase import db
from schemas.risk import (RiskAssessmentResponse,)
from schemas.mother_risk import (MotherRiskAssessmentRequest,)
from schemas.child_risk import (ChildRiskAssessmentRequest,)
from ai.mother_engine import (assess_mother_risk,)
from ai.child_engine import (assess_child_risk,)


COLLECTION = "risk_assessments"


def get_patient(patient_id: str):
    document = (
        db.collection("patients")
        .document(patient_id)
        .get()
    )

    if not document.exists:
        return None

    return document.to_dict()


def create_risk_assessment(
    data: dict,
    assessed_by: str,
) -> RiskAssessmentResponse:

    patient_id = data.get("patient_id")

    if not patient_id:

        raise HTTPException(
            status_code=422,
            detail="patient_id is required.",
        )

    patient = get_patient(patient_id)

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

            assessment_data = (
                MotherRiskAssessmentRequest(
                    **data
                )
            )

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
            child_data = dict(data)
            child_data["age_months"] = child_data.get(
                "child_age_months",
                patient.get("age_months"),
            )
            assessment_data = (
                ChildRiskAssessmentRequest(
                    **child_data
                )
            )

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
    }

    (
        db.collection(COLLECTION)
        .document(assessment_id)
        .set(assessment_record)
    )

    return RiskAssessmentResponse(
        **assessment_record
    )


def get_assessment_history(patient_id: str) -> list[dict]:
    assessments = []
    for document in db.collection(COLLECTION).stream():
        data = document.to_dict()
        if data.get("patient_id") == patient_id:
            assessments.append(data)
    return sorted(
        assessments,
        key=lambda item: item.get("assessed_at", ""),
        reverse=True,
    )


def get_current_risk(patient_id: str) -> dict:
    history = get_assessment_history(patient_id)
    if not history:
        raise HTTPException(status_code=404, detail="No risk assessment found.")
    return history[0]