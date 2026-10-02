from fastapi import APIRouter, Depends, Query
from core.auth import require_role
from schemas.role import UserRole
from services.dashboard_service import DashboardService
from schemas.dashboard import DashboardMetrics, TrendResponse

dashboard_router = APIRouter(
    prefix="/api/v1/dashboard",
    tags=["dashboard"]
)


@dashboard_router.get("/", response_model=DashboardMetrics)
async def get_dashboard(current_user: dict = Depends(require_role([UserRole.ADMIN]))):
    return DashboardService.get_dashboard_metrics()

@dashboard_router.get("/trends", response_model=TrendResponse)
async def get_trends(days: int = Query(7, ge=1, le=90), current_user: dict = Depends(require_role([UserRole.ADMIN]))):
    return DashboardService.get_trends(days=days)
