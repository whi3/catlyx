from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class ReferralCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    patient_id: str = Field(min_length=1, max_length=128)
    reason: str = Field(min_length=3, max_length=1000)
    destination: str = Field(min_length=2, max_length=200)
    urgency: Literal["routine", "urgent", "emergency"] = "routine"
    notes: Optional[str] = Field(default=None, max_length=2000)

class ReferralStatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: Literal["completed", "cancelled"]


class ReferralFollowUpCreate(BaseModel):
    """Compatibility input for clients migrating to the follow-ups API."""
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    notes: Optional[str] = Field(default=None, max_length=2000)
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

    facility_id: Optional[str] = None
