from typing import Optional

from pydantic import BaseModel


class ReferralCreate(BaseModel):
    patient_id: str
    reason: str
    destination: str
    urgency: str = "routine"
    notes: Optional[str] = None

class ReferralStatusUpdate(BaseModel):

    status: str


class FollowUpCreate(BaseModel):

    notes: Optional[str] = None

    completed: bool = False


class ReferralResponse(BaseModel):

    referral_id: str

    patient_id: str

    reason: str

    destination: str

    urgency: str

    status: str

    notes: Optional[str] = None

    created_at: str

    follow_up_required: bool = False

    follow_up_completed: bool = False

    follow_up_notes: Optional[str] = None

    follow_up_date: Optional[str] = None