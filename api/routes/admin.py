from fastapi import Depends, APIRouter

from core.auth import get_current_user, require_role
from schemas.role import UserRole, RoleCreate
from services.role_service import assign_role, get_audit_logs

router=APIRouter(
    prefix="/api/v1/admin",
    tags=["Admin"],
)


@router.post("/assign-role",response_model=dict)
async def assign_user_role(role_assignment:RoleCreate,current_user:dict=Depends(require_role([UserRole.ADMIN])),):
    """Assign a role to a user. Only accessible by Admins."""
    return assign_role(role_assignment.user_id,role_assignment.role)



@router.get("/audit-logs",response_model=list[dict])
async def view_audit_logs(user_id:str=None,current_user:dict=Depends(require_role([UserRole.ADMIN, UserRole.SUPERVISOR])),):
    """View audit logs. Only accessible by Admins and Supervisors."""
    return get_audit_logs(user_id=user_id)