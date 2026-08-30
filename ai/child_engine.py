from schemas.child_risk import (
    ChildRiskAssessmentRequest,
)
from schemas.risk import RiskAssessmentResponse


def assess_child_risk(
    data: ChildRiskAssessmentRequest,
) -> RiskAssessmentResponse:

    score = 0
    reasons = []

    if data.difficulty_breathing:
        score += 3
        reasons.append(
            "Difficulty breathing reported"
        )

    if data.severe_diarrhoea:
        score += 2
        reasons.append(
            "Severe diarrhoea reported"
        )

    if data.persistent_vomiting:
        score += 2
        reasons.append(
            "Persistent vomiting reported"
        )

    if data.feeding_difficulty:
        score += 3
        reasons.append(
            "Feeding difficulty reported"
        )

    if data.lethargy:
        score += 3
        reasons.append(
            "Lethargy reported"
        )

    if data.convulsions:
        score += 5
        reasons.append(
            "Convulsions reported"
        )

    if data.severe_wasting:
        score += 4
        reasons.append(
            "Severe wasting reported"
        )

    if data.missed_immunization:
        score += 1
        reasons.append(
            "Missed immunization reported"
        )

    if (
        data.temperature is not None
        and data.temperature >= 38
    ):
        score += 2
        reasons.append(
            "Elevated temperature reported"
        )

    if score >= 6:

        level = "High Risk"

        recommendation = (
            "Urgent clinical review or referral "
            "should be considered."
        )

    elif score >= 3:

        level = "Moderate Risk"

        recommendation = (
            "Clinical review should be considered "
            "as soon as appropriate."
        )

    else:

        level = "Low Risk"

        recommendation = (
            "Continue routine monitoring "
            "according to applicable guidance."
        )

    return RiskAssessmentResponse(
        patient_id=data.patient_id,
        risk_level=level,
        risk_score=score,
        reasons=reasons,
        recommendation=recommendation,
    )