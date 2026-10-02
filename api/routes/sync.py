from fastapi import APIRouter, Depends, HTTPException
from core.auth import require_staff_role

router = APIRouter(
    prefix="/api/v1/sync",
    tags=["Synchronization"],
)

@router.post("/patients", response_model=dict)
async def synchronize_patients(current_user: dict = Depends(require_staff_role)):
    raise HTTPException(
        status_code=501,
        detail="Patient sync is unavailable until facility-scoped conflict handling is implemented.",
    )
