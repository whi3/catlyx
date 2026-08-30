from schemas.risk import (
    RiskAssessmentRequest,
    RiskAssessmentResponse
)


def assess_risk(
    data: RiskAssessmentRequest,
) -> RiskAssessmentResponse:

    score = 0
    reasons = []

    if data.severe_bleeding:
        score += 4
        reasons.append("Severe bleeding reported")

    if data.severe_headache:
        score += 2
        reasons.append("Severe headache")

    if data.swelling:
        score += 2
        reasons.append("Swelling detected")

    if data.temperature >= 38:
        score += 2
        reasons.append("High temperature")

    if data.missed_follow_up:
        score += 2
        reasons.append("Missed previous follow-up")

    if score >= 6:
        level = "High Risk"
        recommendation = "Refer immediately."

    elif score >= 3:
        level = "Moderate Risk"
        recommendation = "Review within 48 hours."

    else:
        level = "Low Risk"
        recommendation = "Continue routine monitoring."

    return RiskAssessmentResponse(
        risk_level=level,
        risk_score=score,
        reasons=reasons,
        recommendation=recommendation
    )