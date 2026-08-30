from datetime import datetime
from fastapi import APIRouter
from config import settings

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
        "message": "I feel so excited right now ...",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
