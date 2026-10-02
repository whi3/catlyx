from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

class ChildCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    first_name: str = Field(min_length=1, max_length=80)
    last_name: str = Field(min_length=1, max_length=80)
    age_months: int = Field(ge=0, le=59)
    guardian_name: str = Field(min_length=1, max_length=160)
    phone_number: Optional[str] = Field(default=None, pattern=r"^\+?[0-9]{7,15}$")
    community: str = Field(min_length=1, max_length=120)
    weight: float = Field(gt=0, le=40)
    muac: Optional[float] = Field(default=None, gt=0, le=40)
    immunization_complete: bool = False

    @field_validator("first_name", "last_name", "guardian_name", "community")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("This field cannot be blank.")
        return value
