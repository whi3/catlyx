import uuid
from datetime import datetime, timezone
from fastapi import HTTPException

from core.firebase import db
from schemas.role import UserRole


def assign_role(user_id:str, role:UserRole) -> dict:
    """Assign a role to a user."""
    role_doc = db.collection("users").document(user_id).get()

    if not role_doc.exists:
        raise HTTPException(status_code=404, detail="User not found",)
    
    db.collection("users").document(user_id).update({
        "role":user_id,
        "role":role.value,
        "message":"Role assigned successfully",
    })

    return UserRole(user_doc.to_dict().get("role",UserRole.CHPS_WORKER.value))


def log_audit(user_id:str,endpoint:str,method:str,status_code:int,details:dict=None,) -> str:
    """Log audit information for role assignments."""
    log_id=str(uuid.uuid4())
    timestamp=datetime.now(timezone.utc).isoformat()

    audit_data={
        "log_id":log_id,
        "user_id":user_id,
        "endpoint":endpoint,
        "method":method,
        "status_code":status_code,
        "timestamp":timestamp,
        "details":details or {},
    }

    db.collection("audit_logs").document(log_id).set(audit_data)

    return log_id


def get_audit_logs(user_id:str=None,limit:int=100) -> list:
    """Retrieve audit logs, optionally filtered by user_id"""
    query=db.collection("audit_logs")

    if user_id:
        query=query.where("user_id","==",user_id)

    docs=query.limit(limit).stream()

    return [doc.to_dict() for doc in docs]