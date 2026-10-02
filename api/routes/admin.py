from fastapi import Depends, APIRouter, Query, Request

from core.auth import require_role
from schemas.role import UserRole, RoleCreate
from services.role_service import assign_role, get_audit_logs

router=APIRouter(
    prefix="/api/v1/admin",
    tags=["Admin"],
)


@router.post("/assign-role",response_model=dict)
async def assign_user_role(
    role_assignment: RoleCreate,
    request: Request,
    current_user: dict = Depends(require_role([UserRole.ADMIN])),
):
    """Assign a role to a user. Only accessible by Admins."""
    request.state.audit_details = {
        "target_user_id": role_assignment.user_id,
        "assigned_role": role_assignment.role.value,
    }
    return assign_role(
        role_assignment.user_id,
        role_assignment.role,
        assigned_by=current_user["uid"],
        facility_id=role_assignment.facility_id,
    )



@router.get("/audit-logs",response_model=list[dict])
async def view_audit_logs(
    user_id: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    current_user: dict = Depends(require_role([UserRole.ADMIN, UserRole.SUPERVISOR])),
):
    """View audit logs. Only accessible by Admins and Supervisors."""
    return get_audit_logs(
        user_id=user_id,
        limit=limit,
        facility_id=current_user.get("facility_id"),
        is_admin=current_user.get("role") == UserRole.ADMIN.value,
    )
