from fastapi import HTTPException

from core.firebase import db

COLLECTION = "risk_assessments"


def get_assessment_history(patient_id: str) -> list[dict]:
	if db is None:
		raise HTTPException(status_code=503, detail="Database is not configured.")

	return [
		document.to_dict()
		for document in db.collection(COLLECTION).stream()
		if document.to_dict().get("patient_id") == patient_id
	]


def get_current_risk(patient_id: str) -> dict:
	assessments = get_assessment_history(patient_id)
	if not assessments:
		raise HTTPException(status_code=404, detail="Risk assessment not found.")

	return max(assessments, key=lambda assessment: assessment.get("assessed_at", ""))