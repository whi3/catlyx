from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

class MotherCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    first_name: str = Field(min_length=1, max_length=80)
    last_name: str = Field(min_length=1, max_length=80)
    age: int = Field(ge=10, le=60)
    phone_number: Optional[str] = Field(default=None, pattern=r"^\+?[0-9]{7,15}$")
    community: str = Field(min_length=1, max_length=120)
    pregnancy_weeks: int = Field(ge=1, le=45)
    blood_pressure_systolic: Optional[int] = Field(default=None, ge=50, le=300)
    blood_pressure_diastolic: Optional[int] = Field(default=None, ge=30, le=200)
    anc_visits: int = Field(default=0, ge=0, le=20)
    expected_delivery_date: Optional[date] = None

    @field_validator("first_name", "last_name", "community")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("This field cannot be blank.")
        return value

    @model_validator(mode="after")
    def validate_blood_pressure_pair(self):
        systolic = self.blood_pressure_systolic
        diastolic = self.blood_pressure_diastolic
        if (systolic is None) != (diastolic is None):
            raise ValueError("Both blood pressure values must be provided together.")
        if systolic is not None and diastolic is not None and systolic <= diastolic:
            raise ValueError("Systolic pressure must exceed diastolic pressure.")
        return self
