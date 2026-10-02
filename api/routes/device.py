from fastapi import APIRouter, Depends, HTTPException, status

from core.auth import require_staff_role
from schemas.device import DeviceTokenRegistration
from services.push_service import register_device_token

router = APIRouter(prefix="/api/v1/devices", tags=["Devices"])


@router.post("/token", status_code=status.HTTP_204_NO_CONTENT)
async def register_push_token(
    registration: DeviceTokenRegistration,
    current_user: dict = Depends(require_staff_role),
):
    try:
        register_device_token(current_user["uid"], registration.token)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
