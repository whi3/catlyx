from fastapi import APIRouter
from schemas.sync import SyncRequest, SyncResponse
from services.sync_service import sync_patients

router = APIRouter(
    prefix="/api/v1/sync",
    tags=["Synchronization"],
)

@router.post("/patients", response_model=dict)
async def synchronize_patients(request: SyncRequest):
    return sync_patients(request.last_synced_at)
