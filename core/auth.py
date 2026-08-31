from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from firebase_admin import auth

from schemas.role import UserRole
from services.role_service import get_user_role

security = HTTPBearer()

def get_current_user(credentials=Depends(security),)-> dict:
    """Verify firebase token and return user information."""
    token = credentials.credentials
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired authentication token.",
        )


def require_role(required_roles:list[UserRole]):
    """Dependency to check if user has required role"""
    async def check_role(current_user:dict=Depends(get_current_user)) -> dict:
        user_role = get_user_role(current_user["uid"])

        if user_role not in required_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions. Required roles: {[r.value for r in required_roles]}",
            )
        
        return current_user

    return check_role