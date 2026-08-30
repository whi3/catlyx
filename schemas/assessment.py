from pydantic import BaseModel

class AssessmentCreate(BaseModel):
    patient_id: str
    
    severe_bleeding: bool = False
    severe_headache: bool = False
    swelling: bool = False
    temperature: float = 36.5
    missed_follow_up: bool = False