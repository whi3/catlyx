from typing import Optional
from pydantic import BaseModel

class MotherCreate(BaseModel):
    first_name: str
    last_name: str
    age: int
    phone_number: Optional[str] = None
    community: str
    pregnancy_weeks: int
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    anc_visits: int = 0
    expected_delivery_date: Optional[str] = None