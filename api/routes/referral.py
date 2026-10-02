from fastapi import APIRouter, Depends, status
from core.auth import require_staff_role
from schemas.referral import ReferralCreate, ReferralStatusUpdate, ReferralFollowUpCreate
from services.referral_service import (
    create_referral,
    get_referral,
    update_referral_status,
)
from utils.sms_messages import referral_created_message
from services.patient_service import get_patient_phone_number
from services.notification_service import dispatch_referral_sms
from services.followup_service import record_legacy_referral_followup


router = APIRouter(
    prefix="/api/v1/referrals",
    tags=["Referrals"],
)

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_new_referral(
    referral: ReferralCreate,
    current_user: dict = Depends(require_staff_role),
):
    result = create_referral(
        referral,
        created_by=current_user["uid"],
        current_user=current_user,
    )
    phone_number = get_patient_phone_number(
        referral.patient_id
    )
    
    if phone_number:
        message = referral_created_message(
            referral.destination
        )
        result["notification_status"] = await dispatch_referral_sms(
            patient_id=referral.patient_id,
            referral_id=result["referral_id"],
            phone_number=phone_number,
            message=message,
        )
    else:
        result["notification_status"] = "not_available"
    
    return result


@router.get("/{referral_id}", response_model=dict)
async def get_referral_by_id(
    referral_id: str,
    current_user: dict = Depends(require_staff_role),
):
    return get_referral(referral_id, current_user=current_user)


@router.put("/{referral_id}/status", response_model=dict)
async def update_status(
    referral_id: str,
    status_update: ReferralStatusUpdate,
    current_user: dict = Depends(require_staff_role),
):
    return update_referral_status(
        referral_id,
        status_update,
        updated_by=current_user["uid"],
        current_user=current_user,
    )


@router.post("/{referral_id}/follow-up", response_model=dict)
async def add_follow_up(
    referral_id: str,
    follow_up: ReferralFollowUpCreate,
    current_user: dict = Depends(require_staff_role),
):
    return record_legacy_referral_followup(
        referral_id,
        follow_up,
        recorded_by=current_user["uid"],
        current_user=current_user,
    )
