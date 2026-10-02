from fastapi import HTTPException

from schemas.role import UserRole


def ensure_facility_access(record: dict, current_user: dict) -> None:
    """Limit non-admin reads and writes to the caller's provisioned facility."""
    if current_user.get("role") == UserRole.ADMIN.value:
        return

    facility_id = current_user.get("facility_id")
    if not facility_id:
        raise HTTPException(
            status_code=403,
            detail="User account has no facility assignment.",
        )
    if not record or record.get("facility_id") != facility_id:
        # Return 404 so callers cannot probe records at other facilities.
        raise HTTPException(status_code=404, detail="Record not found.")


def facility_query(collection, current_user: dict):
    """Build a Firestore facility filter unless the caller is an admin."""
    if current_user.get("role") == UserRole.ADMIN.value:
        return collection
    facility_id = current_user.get("facility_id")
    if not facility_id:
        raise HTTPException(
            status_code=403,
            detail="User account has no facility assignment.",
        )
    return collection.where("facility_id", "==", facility_id)
