from datetime import datetime, timezone
from firebase_admin import firestore
from schemas.role import UserRole, AuditLog

db = None  # Will be initialized at runtime or mocked in tests


def _get_db():
    """Get or initialize database connection"""
    global db
    if db is None:
        db = firestore.client()
    return db


def assign_role(user_id: str, role: UserRole) -> dict:
    """Assign a role to a user"""
    db_ref = _get_db()
    user_ref = db_ref.collection("users").document(user_id)
    user_doc = user_ref.get()
    
    if not user_doc.exists:
        raise ValueError(f"User {user_id} not found")
    
    user_ref.update({"role": role.value})
    
    return {
        "user_id": user_id,
        "role": role.value,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def get_user_role(user_id: str) -> UserRole:
    """Get user's role from Firestore"""
    try:
        db_ref = _get_db()
        user_doc = db_ref.collection("users").document(user_id).get()
        
        if user_doc.exists:
            role_value = user_doc.get("role")
            if role_value:
                return UserRole(role_value)
        
        return UserRole.CHPS_WORKER  # Default role
    except Exception:
        return UserRole.CHPS_WORKER


def log_audit(
    user_id: str,
    endpoint: str,
    method: str,
    status_code: int,
    details: dict = None,
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
    }
    
    doc_ref = db_ref.collection("audit_logs").add(audit_entry)[1]
    return doc_ref.id


def get_audit_logs(user_id: str = None, limit: int = 100) -> list:
    """Retrieve audit logs, optionally filtered by user"""
    db_ref = _get_db()
    query = db_ref.collection("audit_logs")
    
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
