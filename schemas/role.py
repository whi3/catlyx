from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, model_validator


class UserRole(str, Enum):
    CHPS_WORKER = "CHPS_WORKER"
    SUPERVISOR = "SUPERVISOR"
    ADMIN = "ADMIN"


class RoleCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: str = Field(min_length=1, max_length=128)
    role: UserRole
    facility_id: str | None = Field(default=None, min_length=1, max_length=128)

    @model_validator(mode="after")
    def require_facility_for_staff(self):
        if self.role != UserRole.ADMIN and not self.facility_id:
            raise ValueError("A facility assignment is required for staff roles.")
        return self

class AuditLog(BaseModel):
    log_id:str
    user_id:str
    endpoint:str
    method:str
    status_code:int
    timestamp:str
    details:dict
