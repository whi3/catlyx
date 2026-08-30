from fastapi import APIRouter, Depends
from core.auth import get_current_user
from schemas.referral import (
    ReferralCreate,
    ReferralStatusUpdate,
    FollowUpCreate,
)
from services.referral_service import (
    create_referral,
    get_referral,
    update_referral_status,
    record_follow_up,
)
from services.sms_service import send_sms
from utils.sms_messages import referral_created_message
from services.patient_service import get_patient_phone_number
from schemas.notification import NotificationCreate
from services.notification_service import (
    create_notification,
    update_notification_status,
)


router = APIRouter(
    prefix="/api/v1/referrals",
    tags=["Referrals"],
)

@router.post("/", response_model=dict)
async def create_new_referral(
    referral: ReferralCreate,
    current_user: dict = Depends(get_current_user),
):
    result = create_referral(
        referral,
        created_by=current_user["uid"],
    )
    phone_number = get_patient_phone_number(
        referral.patient_id
    )
    
    if phone_number:
        message = referral_created_message(
            referral.destination
        )
        send_sms(phone_number, message)
    
    return result


@router.get("/{referral_id}", response_model=dict)
async def get_referral_by_id(referral_id: str):
    return get_referral(referral_id)


@router.put("/{referral_id}/status", response_model=dict)
async def update_status(
    referral_id: str,
    status_update: ReferralStatusUpdate,
    current_user: dict = Depends(get_current_user),
):
    return update_referral_status(
        referral_id,
        status_update,
        updated_by=current_user["uid"]
    )


@router.post("/{referral_id}/follow-up", response_model=dict)
async def add_follow_up(
    referral_id: str,
    follow_up: FollowUpCreate,
    current_user: dict = Depends(get_current_user),
):
    return record_follow_up(
        referral_id,
        follow_up,
        recorded_by=current_user["uid"]
    )
