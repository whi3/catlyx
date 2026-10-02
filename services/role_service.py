from datetime import datetime, timezone
import logging
from firebase_admin import firestore
from fastapi import HTTPException
from core.firebase import db as firebase_db
from schemas.role import UserRole

db = firebase_db  # Tests can replace this module-level client.
logger = logging.getLogger(__name__)


def _get_db():
    if db is None:
        raise HTTPException(status_code=503, detail="Database service is not configured.")
    return db


def get_user_profile(user_id: str) -> dict:
    """Load an explicitly provisioned account; unknown users fail closed."""
    try:
        user_doc = _get_db().collection("users").document(user_id).get()
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Could not load the provisioned user profile.")
        raise HTTPException(status_code=503, detail="Identity service is unavailable.") from exc
    if not user_doc.exists:
        raise HTTPException(status_code=403, detail="User account is not provisioned.")

    profile = user_doc.to_dict() or {}
    try:
        profile["role"] = UserRole(profile.get("role"))
    except (TypeError, ValueError):
        raise HTTPException(status_code=403, detail="User role is invalid.")
    return profile


def assign_role(
    user_id: str,
    role: UserRole,
    assigned_by: str,
    facility_id: str | None = None,
) -> dict:
    """Assign a role to a user"""
    db_ref = _get_db()
    user_ref = db_ref.collection("users").document(user_id)
    user_doc = user_ref.get()
    
    if not user_doc.exists:
        raise HTTPException(status_code=404, detail="User account not found.")
    
    if role != UserRole.ADMIN and not facility_id:
        raise HTTPException(status_code=422, detail="A facility is required for staff roles.")
    update = {"role": role.value}
    update["role_updated_by"] = assigned_by
    update["role_updated_at"] = datetime.now(timezone.utc).isoformat()
    if facility_id is not None:
        update["facility_id"] = facility_id
    elif role == UserRole.ADMIN:
        update["facility_id"] = None
    user_ref.update(update)
    
    result = {
        "user_id": user_id,
        "role": role.value,
        "facility_id": facility_id,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    return result


def get_user_role(user_id: str) -> UserRole:
    """Get user's role from Firestore"""
    return get_user_profile(user_id)["role"]


def log_audit(
    user_id: str,
    endpoint: str,
    method: str,
    status_code: int,
    details: dict = None,
    facility_id: str | None = None,
) -> str:
    """Log an audit entry"""
    db_ref = _get_db()
    audit_entry = {
        "user_id": user_id,
        "endpoint": endpoint,
        "method": method,
        "status_code": status_code,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "details": details or {},
        "facility_id": facility_id,
    }
    
    doc_ref = db_ref.collection("audit_logs").add(audit_entry)[1]
    return doc_ref.id


def begin_api_audit(request_id: str, method: str) -> str:
    """Persist an audit marker before an API handler can change data."""
    db_ref = _get_db()
    audit_entry = {
        "user_id": "anonymous",
        "endpoint": "/api/v1",
        "method": method,
        "status_code": 0,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "details": {"request_id": request_id, "state": "started"},
        "facility_id": None,
    }
    return db_ref.collection("audit_logs").add(audit_entry)[1].id


def finish_api_audit(
    audit_id: str,
    *,
    request_id: str,
    endpoint: str,
    status_code: int,
    user_id: str,
    facility_id: str | None,
    role: str | None,
    details: dict | None = None,
) -> None:
    """Complete a previously persisted request marker without storing payloads."""
    db_ref = _get_db()
    db_ref.collection("audit_logs").document(audit_id).update({
        "endpoint": endpoint,
        "status_code": status_code,
        "user_id": user_id,
        "facility_id": facility_id,
        "role": role,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "details": {
            "request_id": request_id,
            "state": "completed",
            **(details or {}),
        },
    })


def get_audit_logs(
    user_id: str | None = None,
    limit: int = 100,
    facility_id: str | None = None,
    is_admin: bool = False,
) -> list:
    """Retrieve audit logs, optionally filtered by user"""
    if not 1 <= limit <= 500:
        raise HTTPException(status_code=422, detail="Audit log limit must be between 1 and 500.")
    if not is_admin and not facility_id:
        raise HTTPException(status_code=403, detail="User account has no facility assignment.")
    db_ref = _get_db()
    query = db_ref.collection("audit_logs")

    if facility_id and not is_admin:
        query = query.where("facility_id", "==", facility_id)
    
    if user_id:
        query = query.where("user_id", "==", user_id)
    
    docs = query.order_by("timestamp", direction=firestore.Query.DESCENDING).limit(limit).stream()
    
    return [
        {
            "log_id": doc.id,
            **doc.to_dict(),
        }
        for doc in docs
    ]
