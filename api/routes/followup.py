from fastapi import APIRouter, Depends, status
from core.auth import require_staff_role
from schemas.followup import(FollowUpOutcome,FollowUpCreate)
from services.followup_service import(get_overdue_followups,get_pending_followups,record_followup_outcome,schedule_followup)


router=APIRouter(
    prefix="/api/v1/followups",
    tags=["Follow-ups"],
)

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_followup(followup: FollowUpCreate, current_user: dict = Depends(require_staff_role)):
    return schedule_followup(
        followup,
        created_by=current_user["uid"],
        current_user=current_user,
    )


@router.get("/pending",response_model=list[dict])
async def pending_followups(current_user: dict = Depends(require_staff_role)):
    return get_pending_followups(current_user)


@router.get("/overdue", response_model=list[dict])
async def overdue_followups(current_user: dict = Depends(require_staff_role)):
    return get_overdue_followups(current_user)


@router.put("/{followup_id}",response_model=dict)
async def update_followup(followup_id: str, outcome: FollowUpOutcome, current_user: dict = Depends(require_staff_role)):
    return record_followup_outcome(
        followup_id,outcome,
        updated_by=current_user["uid"],
        current_user=current_user,
    )
