from fastapi import APIRouter, Depends
from core.auth import get_current_user
from services.risk_service import create_risk_assessment
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
