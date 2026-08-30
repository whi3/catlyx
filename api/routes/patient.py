from fastapi import APIRouter
from fastapi import Depends

from core.auth import get_current_user
from schemas.mother import MotherCreate
from schemas.child import ChildCreate
from schemas.risk import RiskAssessmentRequest

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

@router.post("/mothers")
async def create_mother(
    mother: MotherCreate,
    current_user: dict = Depends(get_current_user),
):
    return register_mother(mother, created_by=current_user["uid"])


@router.post("/children")
async def create_child(
    child: ChildCreate,
    current_user: dict = Depends(get_current_user),
):
    return register_child(child, created_by=current_user["uid"])

@router.get("/")
async def get_patients():
    return get_all_patients()

@router.get("/{patient_id}")
async def get_patient_by_id(patient_id: str):
    return get_patient(patient_id)

@router.post("/assess-risk")
async def assess_patient_risk(
    request: RiskAssessmentRequest,
    current_user: dict = Depends(get_current_user),
):
    # TODO: Implement risk assessment logic
    return {"message": "Risk assessment endpoint - implementation pending"}