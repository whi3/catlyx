from fastapi import APIRouter, Depends, HTTPException
from core.auth import get_current_user
from schemas.sync import SyncRequest, SyncResponse
from services.sync_service import sync_patients

router = APIRouter(
    prefix="/api/v1/sync",
    tags=["Synchronization"],
)

@router.post("/patients", response_model=dict)
async def synchronize_patients(
    request: SyncRequest,
    current_user: dict = Depends(get_current_user),
):
    try:
        return sync_patients(request.last_synced_at)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail="Invalid last_synced_at timestamp.",
        ) from exc
