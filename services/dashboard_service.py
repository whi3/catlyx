from datetime import datetime,timedelta,timezone
from core.firebase import db
from schemas.dashboard import (
    DashboardMetrics,PatientMetrics,RiskDistribution,ReferralMetrics,
    FollowUpMetrics,TrendDataPoint,TrendResponse
)


class DashboardService:
    """Metrics calculation and aggregation"""

    @staticmethod
    def _parse_datetime(value: str) -> datetime:
        """Parse an ISO timestamp and normalize it to UTC."""
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)

    @staticmethod
    def get_patient_metrics():
        """Calculating patient registration metrics"""
        patients = db.collection("patients").stream()

        total_mothers = 0
        total_children = 0
        new_today = 0
        new_this_week = 0

        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = now - timedelta(days=7)

        for doc in patients:
            data = doc.to_dict()
            patient_type = data.get("patient_type", "unknown")
            created_at_str = data.get("created_at")

            if patient_type == "mother":
                total_mothers += 1
            elif patient_type == "child":
                total_children += 1

            if created_at_str:
                try:
                    created_at = DashboardService._parse_datetime(created_at_str)
                    if created_at >= today_start:
                        new_today += 1
                    if created_at >= week_ago:
                        new_this_week += 1
                except:
                    pass

        return PatientMetrics(
            total_mothers=total_mothers,
            total_children=total_children,
            total_patients=total_mothers + total_children,
            new_patients_today=new_today,
            new_patients_this_week=new_this_week
        )

    @staticmethod
    def get_risk_distribution():
        assessments = db.collection("risk_assessments").stream()

        low_count = 0
        moderate_count = 0
        high_count = 0

        for doc in assessments:
            data = doc.to_dict()
            risk_level = data.get("risk_level", "").lower()

            if risk_level == "low risk":
                low_count += 1
            elif risk_level == "moderate risk":
                moderate_count += 1
            elif risk_level == "high risk":
                high_count += 1

        return RiskDistribution(
            low_risk_count=low_count,
            moderate_risk_count=moderate_count,
            high_risk_count=high_count
        )

    @staticmethod
    def get_referral_metrics():
        referrals = db.collection("referrals").stream()

        total = 0
        pending = 0
        completed = 0
        total_hours = 0
        completion_count = 0

        for doc in referrals:
            data = doc.to_dict()
            status = data.get("status", "").lower()

            total += 1

            if status == "pending":
                pending += 1
            elif status == "completed":
                completed += 1
                completion_count += 1
            
            created_str = data.get("created_at")
            completed_str = data.get("completed_at")

            if created_str and completed_str:
                try:
                    created = DashboardService._parse_datetime(created_str)
                    completed_dt = DashboardService._parse_datetime(completed_str)
                    hours = (completed_dt - created).total_seconds() / 3600
                    total_hours += hours
                except:
                    pass

        completion_rate = (completed / total * 100) if total > 0 else 0
        avg_hours = (total_hours / completion_count) if completion_count > 0 else 0

        return ReferralMetrics(
            total_referrals=total,
            pending_referrals=pending,
            completed_referrals=completed,
            completion_rate=round(completion_rate, 1),
            average_completion_time_hours=round(avg_hours, 1)
        )

    @staticmethod
    def get_followup_metrics():
        followups = db.collection("followups").stream()

        total = 0
        pending = 0
        completed = 0
        overdue = 0

        now = datetime.now(timezone.utc)

        for doc in followups:
            data = doc .to_dict()
            status = data.get("status", "").lower()
            scheduled_date_str = data.get("scheduled_date")

            total += 1

            if status == "pending":
                pending += 1

                if scheduled_date_str:
                    try:
                        scheduled = DashboardService._parse_datetime(scheduled_date_str)
                        if scheduled < now:
                            overdue += 1
                    except:
                        pass
            
            elif status == "completed":
                completed += 1

        completion_rate = (completed / total * 100) if total > 0 else 0

        return FollowUpMetrics(
            total_followups=total,
            pending_followups=pending,
            completed_followups=completed,
            overdue_followups=overdue,
            completion_rate=round(completion_rate, 1)
        )

    @staticmethod
    def determine_system_health(metrics: dict) -> str:
        """Determining system health based on metrics."""
        # If no data, consider system HEALTHY
        if metrics["referral_metrics"].total_referrals == 0:
            return "HEALTHY"
        
        # CRITICAL: >5% overdue followups or <50% referral completion
        if metrics["followup_metrics"].overdue_followups > 5:
            return "CRITICAL"
        if metrics["referral_metrics"].completion_rate < 50:
            return "CRITICAL"

        # WARNING: >10% overdue or >20% high-risk patients
        if metrics["followup_metrics"].overdue_followups > 0:
            return "WARNING"
        if metrics["risk_distribution"].high_risk_count > 5:
            return "WARNING"

        return "HEALTHY"

    @staticmethod
    def get_dashboard_metrics() -> DashboardMetrics:
        """Get all dashboard metrics."""
        patient_metrics = DashboardService.get_patient_metrics()
        risk_distribution = DashboardService.get_risk_distribution()
        referral_metrics = DashboardService.get_referral_metrics()
        followup_metrics = DashboardService.get_followup_metrics()

        metrics_dict = {
            "patient_metrics": patient_metrics,
            "risk_distribution": risk_distribution,
            "referral_metrics": referral_metrics,
            "followup_metrics": followup_metrics
        }

        system_health = DashboardService.determine_system_health(metrics_dict)

        return DashboardMetrics(
            timestamp=datetime.now(timezone.utc),
            patient_metrics=patient_metrics,
            risk_distribution=risk_distribution,
            referral_metrics=referral_metrics,
            followup_metrics=followup_metrics,
            system_health=system_health
        )

    def get_trends(days: int = 7):
        data_points = []
        now = datetime.now(timezone.utc)

        for i in range(days,0,-1):
            current_date = now - timedelta(days=i)
            date_str = current_date.date().isoformat()
            day_start = current_date .replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)

            high_risk_count = 0
            assessments = list(db.collection("risk_assessments").stream())
            for doc in assessments:
                data = doc.to_dict()
                created_str = data.get("assessed_at") or data.get("created_at")
                if created_str:
                    try:
                        created = DashboardService._parse_datetime(created_str)
                        if (
                            day_start <= created < day_end
                            and data.get("risk_level", "").lower() == "high risk"
                        ):
                            high_risk_count += 1
                    except:
                        pass

            new_referrals = 0
            referrals = list(db.collection("referrals").stream())
            for doc in referrals:
                data = doc.to_dict()
                created_str = data.get("created_at")
                if created_str:
                    try:
                        created = DashboardService._parse_datetime(created_str)
                        if day_start <= created < day_end:
                            new_referrals += 1
                    except:
                        pass

            completed_referrals = 0
            for doc in referrals:
                data = doc.to_dict()
                completed_str = data.get("completed_at")
                if completed_str:
                    try:
                        completed = DashboardService._parse_datetime(completed_str)
                        if day_start <= completed < day_end:
                            completed_referrals += 1
                    except:
                        pass

            overdue_followups = 0
            followups = db.collection("followups").stream()
            for doc in followups:
                data = doc.to_dict()
                status =  data.get("status", "").lower()
                scheduled_str = data.get("scheduled_date")
                if status == "pending" and scheduled_str:
                    try:
                        scheduled = DashboardService._parse_datetime(scheduled_str)
                        if scheduled < day_start:
                            overdue_followups += 1
                    except:
                        pass

            data_points.append(
                TrendDataPoint(
                    date=date_str,
                    high_risk_count=high_risk_count,
                    new_referrals=new_referrals,
                    completed_referrals=completed_referrals,
                    overdue_followups=overdue_followups
                )
            )
    
        return TrendResponse(
            data_points=data_points,
            date_range=f"last_{days}_days"
        )
