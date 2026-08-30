from pydantic import BaseModel
from typing import Optional

class NotificationCreate(BaseModel):
    patient_id: str
    referral_id: str
    phone_number: str
    message: str

class NotificationResponse(BaseModel):
    notification_id: str
    patient_id: str
    referral_id: str
    phone_number: str
    message: str
    status: str
    created_at: str
    sent_at: Optional[str] = None