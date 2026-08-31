from enum import Enum
from pydantic import BaseModel


class UserRole(str, Enum):
    CHPS_WORKER = "CHPS_WORKER"
    SUPERVISOR = "SUPERVISOR"
    ADMIN = "ADMIN"


class RoleCreate(BaseModel):
    user_id:str
    role:UserRole

class AuditLog(BaseModel):
    log_id:str
    user_id:str
    endpoint:str
    method:str
    status_code:int
    timestamp:str
    details:dict