from fastapi import APIRouter
from api.routes.health import router as health_router
from api.routes.patient import router as patient_router
from api.routes.risk import router as risk_router
from api.routes.referral import router as referral_router
from api.routes.sync import router as sync_router
from api.routes.followup import router as followup_router
from api.routes.admin import router as admin_router
from api.routes.dashboard import dashboard_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(patient_router)
api_router.include_router(risk_router)
api_router.include_router(referral_router)
api_router.include_router(sync_router)
api_router.include_router(followup_router)
api_router.include_router(admin_router)
api_router.include_router(dashboard_router)