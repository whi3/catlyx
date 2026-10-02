from pydantic import BaseModel, ConfigDict, Field


class DeviceTokenRegistration(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    token: str = Field(min_length=20, max_length=4096)
