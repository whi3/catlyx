from pydantic import BaseModel


class MotherRiskAssessmentRequest(BaseModel):
    patient_id: str
    pregnancy_weeks: int
    severe_bleeding: bool = False
    severe_headache: bool = False
    blurred_vision: bool = False
    swelling: bool = False
    severe_abdominal_pain: bool = False
    fever: bool = False
    difficulty_breathing: bool = False
    reduced_fetal_movement: bool = False
    missed_anc: bool = False