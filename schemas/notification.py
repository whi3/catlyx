from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class NotificationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    patient_id: str = Field(min_length=1, max_length=128)
    referral_id: str = Field(min_length=1, max_length=128)
    phone_number: str = Field(pattern=r"^\+?[0-9]{7,15}$")
    message: str = Field(min_length=1, max_length=1000)

class NotificationResponse(BaseModel):
    notification_id: str
    patient_id: str
    referral_id: str
    phone_number: str
    message: str
    status: str
    created_at: str
    sent_at: Optional[str] = None
