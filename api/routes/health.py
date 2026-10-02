import logging
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from config import settings
from core.firebase import get_db

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/health",
    tags=["Health"]
)

@router.get("/")
async def health_checker():
    return {
        "status": "I'm good",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "message": "Service is running.",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/ready")
async def readiness_check():
    """Check that the API can reach its required database dependency."""
    try:
        get_db().collection("patients").limit(1).get()
    except Exception as exc:
        logger.warning("Readiness check failed for a required dependency.")
        raise HTTPException(status_code=503, detail="Service is not ready.") from exc
    return {"status": "ready", "timestamp": datetime.now(timezone.utc).isoformat()}
