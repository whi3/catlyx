from typing import Optional

from pydantic import BaseModel, EmailStr

class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    
    age: int
    phone_number: Optional[str] = None 
    community: str
    is_pregnant: bool = False
    pregnancy_weeks: Optional[str] = None
    child_age_months: Optional[int] = None
    emergency_contact: Optional[str] = None
    
class PatientResponse(BaseModel):
    patient_id: str
    message: str