from pydantic import BaseModel, ConfigDict, Field


class MotherRiskAssessmentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    patient_id: str
    pregnancy_weeks: int = Field(ge=1, le=45)
    severe_bleeding: bool = False
    convulsions: bool = False
    severe_headache: bool = False
    blurred_vision: bool = False
    swelling: bool = False
    severe_abdominal_pain: bool = False
    fever: bool = False
    difficulty_breathing: bool = False
    reduced_fetal_movement: bool = False
    missed_anc: bool = False
