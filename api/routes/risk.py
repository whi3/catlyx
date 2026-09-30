from fastapi import APIRouter, Depends
from core.auth import get_current_user
from services.risk_service import (
    create_risk_assessment,
    get_assessment_history,
    get_current_risk,
)
from schemas.risk import RiskAssessmentRequest

router = APIRouter(
    prefix="/api/v1/risk-assessment",
    tags=["Risk Assessment"],
)


@router.post("/")
async def assess_patient_risk(
    request: RiskAssessmentRequest,
    current_user: dict = Depends(
        get_current_user
    ),
):
    return create_risk_assessment(
        request.model_dump(),
        assessed_by=current_user["uid"],
    )


patient_router = APIRouter(prefix="/api/v1/patients", tags=["Risk Assessment"])


@patient_router.get("/{patient_id}/risk")
async def current_patient_risk(
    patient_id: str,
    current_user: dict = Depends(get_current_user),
):
    return get_current_risk(patient_id)


@patient_router.get("/{patient_id}/assessments")
async def patient_assessment_history(
    patient_id: str,
    current_user: dict = Depends(get_current_user),
):
    return get_assessment_history(patient_id)
