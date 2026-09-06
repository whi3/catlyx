import firebase_admin
from firebase_admin import credentials, firestore
from pathlib import Path

from config import settings

db = None

if settings.FIREBASE_CREDENTIALS and Path(settings.FIREBASE_CREDENTIALS).is_file():
    if not firebase_admin._apps:
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS)
        firebase_admin.initialize_app(cred)
    db = firestore.client()