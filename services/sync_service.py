from datetime import datetime, timezone
from core.firebase import db

PATIENT_COLLECTION = "patients"

def get_updated_patients(last_synced_at: str,):
    last_sync = datetime.fromisoformat(
        last_synced_at.replace("Z", "+00:00")
    )

    documents = (db.collection(PATIENT_COLLECTION).stream())
    patients = []
    for document in documents:
        data = document.to_dict()
        updated_at = data.get("updated_at")
        if not updated_at:
            continue
        updated_time = datetime.fromisoformat(
            updated_at.replace("Z", "+00:00")
        )

        if updated_time > last_sync:
            patients.append(data)

    return patients


def sync_patients(last_synced_at: str,):

    patients = get_updated_patients(
        last_synced_at
    )

    synced_at = (
        datetime.now(timezone.utc)
        .isoformat()
    )

    return {
        "synced_at": synced_at,
        "patients": patients,
    }