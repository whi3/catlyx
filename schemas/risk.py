from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator


class RiskAssessmentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    patient_id: str = Field(
        ...,
        description="Unique patient ID"
    )

    age: Optional[int] = Field(default=None, ge=0, le=120)

    pregnancy_weeks: Optional[int] = Field(
        default=None,
        ge=1,
        le=45,
        description="Weeks of pregnancy"
    )

    child_age_months: Optional[int] = Field(default=None, ge=0, le=59, description="Child age in months")
    temperature: Optional[float] = Field(default=None, ge=30, le=45)

    systolic_bp: Optional[int] = Field(default=None, ge=50, le=300)
    diastolic_bp: Optional[int] = Field(default=None, ge=30, le=200)
    weight: Optional[float] = Field(default=None, gt=0, le=300)
    severe_bleeding: bool = False
    severe_headache: bool = False
    swelling: bool = False
    fever: bool = False
    missed_follow_up: bool = False
    blurred_vision: bool = False
    severe_abdominal_pain: bool = False
    difficulty_breathing: bool = False
    reduced_fetal_movement: bool = False
    missed_anc: bool = False
    severe_diarrhoea: bool = False
    persistent_vomiting: bool = False
    feeding_difficulty: bool = False
    lethargy: bool = False
    convulsions: bool = False
    severe_wasting: bool = False
    missed_immunization: bool = False

    @model_validator(mode="after")
    def validate_blood_pressure_pair(self):
        if (self.systolic_bp is None) != (self.diastolic_bp is None):
            raise ValueError("Both blood pressure values must be provided together.")
        if (
            self.systolic_bp is not None
            and self.diastolic_bp is not None
            and self.systolic_bp <= self.diastolic_bp
        ):
            raise ValueError("Systolic pressure must exceed diastolic pressure.")
        return self

class RiskAssessmentResponse(BaseModel):
    assessment_id: Optional[str] = None
    patient_id: str
    risk_level: str
    risk_score: int
    reasons: list[str]
    recommendation: str
    assessed_by: Optional[str] = None
    assessed_at: Optional[str] = None
    observations: dict = Field(default_factory=dict)
    engine_version: str = "rules-v1"
    clinical_validation_status: str = "pending"
    decision_support_only: bool = True
