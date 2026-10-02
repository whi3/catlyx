from fastapi import APIRouter, Depends, Query, Response
from core.auth import require_staff_role
from services.risk_service import (
    create_risk_assessment,
    get_patient,
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
    current_user: dict = Depends(require_staff_role),
):
    return create_risk_assessment(
        request.model_dump(exclude_unset=True),
        assessed_by=current_user["uid"],
        current_user=current_user,
    )


patient_router = APIRouter(prefix="/api/v1/patients", tags=["Risk Assessment"])


@patient_router.get("/{patient_id}/risk")
async def current_patient_risk(
    patient_id: str,
    current_user: dict = Depends(require_staff_role),
):
    get_patient(patient_id, current_user=current_user)
    return get_current_risk(patient_id)


@patient_router.get("/{patient_id}/assessments")
async def patient_assessment_history(
    patient_id: str,
    response: Response,
    limit: int = Query(default=50, ge=1, le=100),
    cursor: str | None = None,
    current_user: dict = Depends(require_staff_role),
):
    get_patient(patient_id, current_user=current_user)
    assessments, next_cursor = get_assessment_history(
        patient_id,
        limit=limit,
        cursor=cursor,
    )
    if next_cursor:
        response.headers["X-Next-Cursor"] = next_cursor
    return assessments
