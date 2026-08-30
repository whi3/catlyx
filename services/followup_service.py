import uuid
from datetime import datetime
from fastapi import HTTPException
from core.firebase import db
from schemas.followup import FollowUpCreate, FollowUpOutcome, FollowUpResponse


COLLECTIONS = "followups"

def _get_followup(followup_id: str):
    document = db.collection(COLLECTIONS).document(followup_id).get()

    if not document.exists:
        raise HTTPException(status_code=404, detail="Follow-up not found")
    
    return document.to_dict()

def schedule_followup(followup: FollowUpCreate, created_by: str):
    referral = (db.collection("referrals").document(followup.referral_id).get())

    if not referral.exists:
        raise HTTPException(status_code=404, detail="Referral not found")

    followup_id = str(uuid.uuid4())
    created_by = datetime.now().isoformat()
    