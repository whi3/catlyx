from fastapi import APIRouter, Depends, status

from core.auth import require_staff_role
from schemas.mother import MotherCreate
from schemas.child import ChildCreate

from services.patient_service import (
    register_mother,
    register_child,
    get_patient,
    get_all_patients,
)


router = APIRouter(
    prefix="/api/v1/patients",
    tags=["Patients"]
)

@router.post("/mothers", status_code=status.HTTP_201_CREATED)
async def create_mother(
    mother: MotherCreate,
    current_user: dict = Depends(require_staff_role),
):
    return register_mother(
        mother,
        created_by=current_user["uid"],
        facility_id=current_user.get("facility_id"),
    )


@router.post("/children", status_code=status.HTTP_201_CREATED)
async def create_child(child: ChildCreate, current_user: dict = Depends(require_staff_role)):
    return register_child(
        child,
        created_by=current_user["uid"],
        facility_id=current_user.get("facility_id"),
    )

@router.get("/")
async def get_patients(current_user: dict = Depends(require_staff_role)):
    return get_all_patients(current_user)

@router.get("/{patient_id}")
async def get_patient_by_id(patient_id: str, current_user: dict = Depends(require_staff_role)):
    return get_patient(patient_id, current_user=current_user)
