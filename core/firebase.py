import firebase_admin
from firebase_admin import credentials, firestore
from fastapi import HTTPException
from pathlib import Path

from config import settings

db = None

if settings.FIREBASE_CREDENTIALS:
    if not Path(settings.FIREBASE_CREDENTIALS).is_file():
        raise RuntimeError("Configured Firebase credentials file does not exist.")
    if not firebase_admin._apps:
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS)
        firebase_admin.initialize_app(cred)
    db = firestore.client()
elif settings.FIREBASE_PROJECT_ID:
    if not firebase_admin._apps:
        firebase_admin.initialize_app(
            options={"projectId": settings.FIREBASE_PROJECT_ID}
        )
    db = firestore.client()
elif firebase_admin._apps:
    db = firestore.client()


def get_db():
    """Return Firestore or fail with a clear service-unavailable response."""
    if db is None:
        raise HTTPException(
            status_code=503,
            detail="Database service is not configured.",
        )
    return db
