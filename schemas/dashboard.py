from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class RiskDistribution(BaseModel):
    low_risk_count: int
    moderate_risk_count: int
    high_risk_count: int

class PatientMetrics(BaseModel):
    total_mothers: int
    total_children: int
    total_patients: int
    new_patients_today:int
    new_patients_this_week:int

class ReferralMetrics(BaseModel):
    total_referrals: int
    pending_referrals: int
    completed_referrals: int
    completion_rate: float
    average_completion_time_hours: float


class FollowUpMetrics(BaseModel):
    total_followups: int
    pending_followups: int
    completed_followups: int
    overdue_followups: float
    completion_rate: float

class DashboardMetrics(BaseModel):
    timestamp: datetime
    patient_metrics: PatientMetrics
    risk_distribution: RiskDistribution
    referral_metrics: ReferralMetrics
    followup_metrics: FollowUpMetrics
    system_health: str

class TrendDataPoint(BaseModel):
    date: str
    high_risk_count: int
    new_referrals: int
    completed_referrals: int
    overdue_followups: int

class TrendResponse(BaseModel):
    data_points: list[TrendDataPoint]
    data_range: str