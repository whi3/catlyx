from typing import Optional
from pydantic import BaseModel

class ChildCreate(BaseModel):
    first_name: str
    last_name: str
    age_months: int
    guardian_name: str
    phone_number: Optional[str] = None
    community: str
    weight: float
    muac: Optional[float] = None
    immunization_complete: bool = False