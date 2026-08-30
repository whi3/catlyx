from typing import List, Optional
from pydantic import BaseModel, Field


class RiskAssessmentRequest(BaseModel):
    patient_id: str = Field(
        ...,
        description="Unique patient ID"
    )

    age: int = Field(..., ge=0)

    pregnancy_weeks: Optional[int] = Field(
        default=None,
        ge=0,
        le=45,
        description="Weeks of pregnancy"
    )

    child_age_months: Optional[int] = Field(default=None,ge=0,le=60,description="Child age in months")
    temperature: float = Field(...,ge=30,le=45)

    systolic_bp: Optional[int] = None
    diastolic_bp: Optional[int] = None
    weight: float = Field(..., gt=0)
    severe_bleeding: bool = False
    severe_headache: bool = False
    swelling: bool = False
    fever: bool = False
    missed_follow_up: bool = False

class RiskAssessmentResponse(BaseModel):
    assessment_id: Optional[str] = None
    patient_id: str
    risk_level: str
    risk_score: int
    reasons: list[str]
    recommendation: str
    assessed_by: Optional[str] = None
    assessed_at: Optional[str] = None