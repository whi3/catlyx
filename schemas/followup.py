from datetime import datetime, timezone
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class FollowUpCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    referral_id: str = Field(min_length=1, max_length=128)
    patient_id: str = Field(min_length=1, max_length=128)
    scheduled_date: datetime
    notes: Optional[str] = Field(default=None, max_length=2000)

    @field_validator("scheduled_date")
    @classmethod
    def require_future_timezone_aware_date(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("scheduled_date must include a timezone.")
        if value.astimezone(timezone.utc) <= datetime.now(timezone.utc):
            raise ValueError("scheduled_date must be in the future.")
        return value

class FollowUpOutcome(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    status: Literal["completed", "missed"]
    outcome: Optional[str] = Field(default=None, max_length=1000)
    notes: Optional[str] = Field(default=None, max_length=2000)

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
