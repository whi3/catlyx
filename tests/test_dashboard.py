"""Dashboard and analytics tests."""

import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from main import app
from core.firebase import db


# Mock Firestore fixtures
class FakeDocument:
    def __init__(self, data):
        self._data = data
    
    def to_dict(self):
        return self._data


class FakeQuery:
    def __init__(self, docs):
        self.docs = docs
    
    def stream(self):
        return iter(self.docs)


class FakeCollection:
    def __init__(self):
        self.docs = {}
    
    def stream(self):
        return iter([FakeDocument(doc) for doc in self.docs.values()])


class FakeDb:
    def __init__(self):
        self.collections = {}
    
    def collection(self, name):
        if name not in self.collections:
            self.collections[name] = FakeCollection()
        return self.collections[name]


@pytest.fixture
def fake_db(monkeypatch):
    """Mock Firestore database."""
    fake = FakeDb()
    monkeypatch.setattr("services.dashboard_service.db", fake)
    return fake


@pytest.fixture
def client():
    """Test client."""
    return TestClient(app)


def create_token():
    """Create a mock Firebase token."""
    return "mock_token_valid"


@pytest.fixture
def mock_auth(monkeypatch):
    """Mock Firebase authentication."""
    def mock_get_current_user(credentials):
        return {"uid": "test_user", "email": "test@example.com"}
    
    monkeypatch.setattr("core.auth.get_current_user", mock_get_current_user)


def test_dashboard_empty_database(fake_db, client, mock_auth):
    """Test dashboard with empty database."""
    fake_db.collection("patients").docs = {}
    fake_db.collection("risk_assessments").docs = {}
    fake_db.collection("referrals").docs = {}
    fake_db.collection("followups").docs = {}
    
    response = client.get("/api/v1/dashboard/")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["patient_metrics"]["total_patients"] == 0
    assert data["risk_distribution"]["low_risk_count"] == 0
    assert data["system_health"] == "HEALTHY"


def test_dashboard_with_patients(fake_db, client, mock_auth):
    """Test dashboard with patient data."""
    now = datetime.now(timezone.utc).isoformat()
    
    fake_db.collection("patients").docs = {
        "p1": {
            "patient_type": "mother",
            "created_at": now,
            "name": "Jane Doe"
        },
        "p2": {
            "patient_type": "child",
            "created_at": now,
            "name": "John Doe"
        }
    }
    fake_db.collection("risk_assessments").docs = {}
    fake_db.collection("referrals").docs = {}
    fake_db.collection("followups").docs = {}
    
    response = client.get("/api/v1/dashboard/")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["patient_metrics"]["total_mothers"] == 1
    assert data["patient_metrics"]["total_children"] == 1
    assert data["patient_metrics"]["total_patients"] == 2
    assert data["patient_metrics"]["new_patients_today"] >= 1


def test_dashboard_with_risk_assessments(fake_db, client, mock_auth):
    """Test dashboard with risk assessment data."""
    fake_db.collection("patients").docs = {}
    fake_db.collection("risk_assessments").docs = {
        "r1": {
            "patient_id": "p1",
            "risk_level": "Low Risk",
            "risk_score": 2,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        "r2": {
            "patient_id": "p2",
            "risk_level": "Moderate Risk",
            "risk_score": 4,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        "r3": {
            "patient_id": "p3",
            "risk_level": "High Risk",
            "risk_score": 8,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    }
    fake_db.collection("referrals").docs = {}
    fake_db.collection("followups").docs = {}
    
    response = client.get("/api/v1/dashboard/")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["risk_distribution"]["low_risk_count"] == 1
    assert data["risk_distribution"]["moderate_risk_count"] == 1
    assert data["risk_distribution"]["high_risk_count"] == 1


def test_dashboard_referral_metrics(fake_db, client, mock_auth):
    """Test dashboard referral completion rate."""
    now = datetime.now(timezone.utc)
    past = (now - timedelta(hours=24)).isoformat()
    
    fake_db.collection("patients").docs = {}
    fake_db.collection("risk_assessments").docs = {}
    fake_db.collection("referrals").docs = {
        "ref1": {
            "patient_id": "p1",
            "status": "completed",
            "created_at": past,
            "completed_at": now.isoformat()
        },
        "ref2": {
            "patient_id": "p2",
            "status": "pending",
            "created_at": past,
            "completed_at": None
        }
    }
    fake_db.collection("followups").docs = {}
    
    response = client.get("/api/v1/dashboard/")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["referral_metrics"]["total_referrals"] == 2
    assert data["referral_metrics"]["pending_referrals"] == 1
    assert data["referral_metrics"]["completed_referrals"] == 1
    assert data["referral_metrics"]["completion_rate"] == 50.0


def test_dashboard_followup_metrics(fake_db, client, mock_auth):
    """Test dashboard follow-up compliance."""
    now = datetime.now(timezone.utc)
    past_date = (now - timedelta(days=2)).date().isoformat()
    future_date = (now + timedelta(days=2)).date().isoformat()
    
    fake_db.collection("patients").docs = {}
    fake_db.collection("risk_assessments").docs = {}
    fake_db.collection("referrals").docs = {}
    fake_db.collection("followups").docs = {
        "fu1": {
            "referral_id": "ref1",
            "patient_id": "p1",
            "status": "completed",
            "scheduled_date": past_date
        },
        "fu2": {
            "referral_id": "ref2",
            "patient_id": "p2",
            "status": "pending",
            "scheduled_date": future_date
        },
        "fu3": {
            "referral_id": "ref3",
            "patient_id": "p3",
            "status": "pending",
            "scheduled_date": past_date
        }
    }
    
    response = client.get("/api/v1/dashboard/")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["followup_metrics"]["total_followups"] == 3
    assert data["followup_metrics"]["pending_followups"] == 2
    assert data["followup_metrics"]["completed_followups"] == 1
    assert data["followup_metrics"]["overdue_followups"] == 1


def test_dashboard_trends(fake_db, client, mock_auth):
    """Test trend data endpoint."""
    now = datetime.now(timezone.utc)
    
    fake_db.collection("patients").docs = {}
    fake_db.collection("risk_assessments").docs = {
        "r1": {
            "risk_level": "High Risk",
            "created_at": now.isoformat()
        }
    }
    fake_db.collection("referrals").docs = {
        "ref1": {
            "created_at": now.isoformat(),
            "completed_at": None
        }
    }
    fake_db.collection("followups").docs = {}
    
    response = client.get("/api/v1/dashboard/trends?days=7")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "data_points" in data
    assert data["date_range"] == "last_7_days"
    assert len(data["data_points"]) == 7


def test_dashboard_system_health_critical(fake_db, client, mock_auth):
    """Test system health determination (CRITICAL)."""
    now = datetime.now(timezone.utc)
    past_date = (now - timedelta(days=5)).date().isoformat()
    
    fake_db.collection("patients").docs = {}
    fake_db.collection("risk_assessments").docs = {}
    fake_db.collection("referrals").docs = {
        "ref1": {"status": "pending", "created_at": now.isoformat()}
    }
    # Add overdue followups to trigger CRITICAL
    fake_db.collection("followups").docs = {
        f"fu{i}": {
            "status": "pending",
            "scheduled_date": past_date
        } for i in range(1, 8)  # 7 overdue
    }
    
    response = client.get("/api/v1/dashboard/")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["system_health"] == "CRITICAL"


def test_dashboard_authentication_required(client):
    """Test that dashboard requires authentication."""
    response = client.get("/api/v1/dashboard/")
    
    assert response.status_code == 403  # or 401, depending on auth implementation

    