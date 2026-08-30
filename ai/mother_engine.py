from schemas.mother_risk import (
    MotherRiskAssessmentRequest,
)
from schemas.risk import RiskAssessmentResponse


def assess_mother_risk(
    data: MotherRiskAssessmentRequest,
) -> RiskAssessmentResponse:

    score = 0
    reasons = []

    if data.severe_bleeding:
        score += 4
        reasons.append(
            "Severe bleeding reported"
        )

    if data.severe_headache:
        score += 2
        reasons.append(
            "Severe headache reported"
        )

    if data.blurred_vision:
        score += 2
        reasons.append(
            "Blurred vision reported"
        )

    if data.swelling:
        score += 2
        reasons.append(
            "Swelling reported"
        )

    if data.severe_abdominal_pain:
        score += 3
        reasons.append(
            "Severe abdominal pain reported"
        )

    if data.fever:
        score += 2
        reasons.append(
            "Fever reported"
        )

    if data.difficulty_breathing:
        score += 3
        reasons.append(
            "Difficulty breathing reported"
        )

    if data.reduced_fetal_movement:
        score += 4
        reasons.append(
            "Reduced fetal movement reported"
        )

    if data.missed_anc:
        score += 1
        reasons.append(
            "Missed ANC visit reported"
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