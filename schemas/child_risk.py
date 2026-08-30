from pydantic import BaseModel


class ChildRiskAssessmentRequest(BaseModel):
    patient_id: str
    age_months: int
    temperature: float | None = None
    difficulty_breathing: bool = False
    severe_diarrhoea: bool = False
    persistent_vomiting: bool = False
    feeding_difficulty: bool = False
    lethargy: bool = False
    convulsions: bool = False
    severe_wasting: bool = False
    missed_immunization: bool = False