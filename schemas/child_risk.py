from pydantic import BaseModel, ConfigDict, Field


class ChildRiskAssessmentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    patient_id: str
    age_months: int = Field(ge=0, le=59)
    temperature: float | None = Field(default=None, ge=30, le=45)
    difficulty_breathing: bool = False
    severe_diarrhoea: bool = False
    persistent_vomiting: bool = False
    feeding_difficulty: bool = False
    lethargy: bool = False
    convulsions: bool = False
    severe_wasting: bool = False
    missed_immunization: bool = False
