from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer
import firebase_admin
from firebase_admin import auth

from schemas.role import UserRole
from services.role_service import get_user_profile

security = HTTPBearer(auto_error=False)

def get_current_user(request: Request, credentials=Depends(security)) -> dict:
    """Verify firebase token and return user information."""
    if not firebase_admin._apps:
        raise HTTPException(status_code=503, detail="Firebase Authentication is not configured.")
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication credentials are required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    try:
        decoded_token = auth.verify_id_token(token)
        request.state.actor_uid = decoded_token["uid"]
        return decoded_token
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired authentication token.",
        )


def require_role(required_roles:list[UserRole]):
    """Dependency to check if user has required role"""
    async def check_role(
        request: Request,
        current_user: dict = Depends(get_current_user),
    ) -> dict:
        profile = get_user_profile(current_user["uid"])
        user_role = profile["role"]

        if user_role not in required_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions. Required roles: {[r.value for r in required_roles]}",
            )
        
        request.state.actor_facility_id = profile.get("facility_id")
        request.state.actor_role = user_role.value
        return {
            **current_user,
            "role": user_role.value,
            "facility_id": profile.get("facility_id"),
        }
    return check_role

require_staff_role = require_role(list(UserRole))
