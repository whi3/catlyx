import logging
from uuid import uuid4
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from config import settings
from api.router import api_router
from services.role_service import begin_api_audit, finish_api_audit

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Offline-first AI-assisted decision support API for CHPS workers."
)

app.include_router(api_router)


@app.middleware("http")
async def audit_api_requests(request: Request, call_next):
    if not request.url.path.startswith("/api/v1/"):
        return await call_next(request)

    request_id = str(uuid4())
    try:
        audit_id = begin_api_audit(request_id, request.method)
    except Exception:
        logger.exception("Could not persist the API audit marker; request denied.")
        return JSONResponse(
            status_code=503,
            content={"detail": "Audit service is unavailable."},
        )

    request.state.audit_record_id = audit_id
    try:
        response = await call_next(request)
    except Exception:
        response = None
        raise
    finally:
        route = request.scope.get("route")
        endpoint = getattr(route, "path", "/unmatched")
        try:
            finish_api_audit(
                audit_id,
                request_id=request_id,
                endpoint=endpoint,
                status_code=response.status_code if response is not None else 500,
                user_id=getattr(request.state, "actor_uid", "anonymous"),
                facility_id=getattr(request.state, "actor_facility_id", None),
                role=getattr(request.state, "actor_role", None),
                details=getattr(request.state, "audit_details", None),
            )
        except Exception:
            # The durable started marker remains available for audit review.
            logger.exception("Could not complete the API audit marker.")
    response.headers["X-Request-ID"] = request_id
    return response

@app.get("/")
def root():
    return {
        "message": "Welcome to CatalystCare API",
        "version": settings.APP_VERSION
    }
