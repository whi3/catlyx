from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Literal, Optional

class NotificationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    patient_id: str = Field(min_length=1, max_length=128)
    referral_id: str = Field(min_length=1, max_length=128)
    channel: Literal["sms", "push"] = "sms"
    phone_number: Optional[str] = Field(default=None, pattern=r"^\+?[0-9]{7,15}$")
    device_token: Optional[str] = Field(default=None, min_length=20, max_length=4096)
    title: Optional[str] = Field(default=None, max_length=120)
    message: str = Field(min_length=1, max_length=1000)

    @model_validator(mode="after")
    def require_channel_target(self):
        if self.channel == "sms" and not self.phone_number:
            raise ValueError("SMS notifications require a phone number.")
        if self.channel == "push" and not self.device_token:
            raise ValueError("Push notifications require a device token.")
        return self

class NotificationResponse(BaseModel):
    notification_id: str
    patient_id: str
    referral_id: str
    phone_number: str
    message: str
    status: str
    created_at: str
    sent_at: Optional[str] = None
