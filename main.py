from fastapi import FastAPI
from config import settings
from api.router import api_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Offline-first AI-assisted decision support API for CHPS workers."
)

app.include_router(api_router)

@app.get("/")
def root():
    return {
        "message": "Welcome to CatalystCare API",
        "version": settings.APP_VERSION
    }