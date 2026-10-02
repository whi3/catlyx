from datetime import datetime, timezone
from core.firebase import db

PATIENT_COLLECTION = "patients"
#--------------------------------------------------------------------------------------

def _parse_timestamp(value: str) -> datetime:
    timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))

    if timestamp.tzinfo is None:
        return timestamp.replace(tzinfo=timezone.utc)
    
    return timestamp.replace(tzinfo=timezone.utc)

#--------------------------------------------------------------------------------------
def get_updated_patients(last_synced_at: str,):
    last_sync = _parse_timestamp(last_synced_at)
    patients = []

    for document in db.collection(PATIENT_COLLECTION).stream():
        data = document.to_dict()
        updated_at = data.get("updated_at")
        if updated_at and _parse_timestamp(updated_at) > last_sync:
            patients.append(data)

    return patients


#----------------------------------------------------------------------------------------
def apply_patient_change(patient_changes: list[dict]) -> tuple[list[dict], list[dict]]:
    sync_results = []
    conflicts = []

    for change in patient_changes:
        patient_id = change.get("patient_id")
        updated_at = change.get("updated_at")
        # Process each patient change

        if not patient_id or not updated_at:
            sync_results.append({
                "patient_id": patient_id,
                "status": "rejected",
                "reason": "patient_id and updated_at are required",
            })
            continue

        client_updated_at = _parse_timestamp(updated_at)
        document = db.collection(PATIENT_COLLECTION).document(patient_id)
        snapshot = document.get()
        server_record = snapshot.to_dict() if snapshot.exists else None
        server_updated_at = (server_record or {}).get("updated_at")

        if server_updated_at and _parse_timestamp(server_updated_at) > client_updated_at:
            conflicts.append({
                "patient_id": patient_id,
                "status": "conflict",
                "resolution": "server_newer",
                "server_record": server_record,
            })      
            continue

        record = dict(server_record or {})
        record.update(change)
        record["patient_id"] = patient_id
        record["sync_timestamp"] = datetime.now(timezone.utc).isoformat()
        record["conflict_state"] = None
        document.set(record)
        sync_results.append({
            "patient_id": patient_id,
            "status": "synced",
        })

    return sync_results, conflicts


#----------------------------------------------------------------------------------------
def sync_patients(last_synced_at: str, patient_changes: list[dict] | None = None):
    sync_results, conflicts = apply_patient_change(patient_changes or [])
    patients = get_updated_patients(last_synced_at)

    return {
        "synced_at": datetime.now(timezone.utc).isoformat(),
        "patients": patients,
        "sync_results": sync_results,
        "conflicts": conflicts,
    }



#---------------------------------------------------------------------------------------
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