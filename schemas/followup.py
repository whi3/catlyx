from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class FollowUpCreate(BaseModel):
    referral_id: str
    patient_id: str
    scheduled_date: datetime
    notes: Optional[str] = None

class FollowUpOutcome(BaseModel):
    status: str = Field(..., pattern="^(pending|completed|missed)$")
    outcome: Optional[str] = None
    notes: Optional[str] = None

class FollowUpResponse(BaseModel):
    followup_id: str
    referral_id: str
    patient_id: str
    scheduled_date: datetime
    status: str
    outcome: Optional[str] = None
    notes: Optional[str] = None
    completed_at: Optional[datetime] = None
    created_by: str