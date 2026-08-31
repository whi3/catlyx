# tests/test_followups.py
import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient

from core.auth import get_current_user
from main import app
from services import followup_service, referral_service, patient_service


class FakeSnapshot:
    def __init__(self, data=None):
        self._data = data

    @property
    def exists(self):
        return self._data is not None

    def to_dict(self):
        return self._data


class FakeDocument:
    def __init__(self, collection, document_id):
        self.collection = collection
        self.document_id = document_id

    def get(self):
        return FakeSnapshot(self.collection.records.get(self.document_id))

    def set(self, data):
        self.collection.records[self.document_id] = dict(data)

    def update(self, data):
        if self.document_id in self.collection.records:
            self.collection.records[self.document_id].update(data)

    def delete(self):
        if self.document_id in self.collection.records:
            del self.collection.records[self.document_id]


class FakeCollection:
    def __init__(self):
        self.records = {}

    def document(self, document_id):
        return FakeDocument(self, document_id)

    def stream(self):
        return [FakeSnapshot(data) for data in self.records.values()]


class FakeFirestore:
    def __init__(self):
        self.collections = {}

    def collection(self, name):
        return self.collections.setdefault(name, FakeCollection())


@pytest.fixture
def client(monkeypatch):
    fake_db = FakeFirestore()
    monkeypatch.setattr(followup_service, "db", fake_db)
    monkeypatch.setattr(referral_service, "db", fake_db)
    monkeypatch.setattr(patient_service, "db", fake_db)
    app.dependency_overrides[get_current_user] = lambda: {"uid": "test-user"}

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_schedule_followup_for_referral(client):
    # Create a referral first
    referral_service.db.collection("referrals").document("ref-1").set({
        "referral_id": "ref-1",
        "patient_id": "patient-1",
        "status": "pending",
    })

    scheduled_date = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()

    response = client.post(
        "/api/v1/followups/",
        json={
            "referral_id": "ref-1",
            "patient_id": "patient-1",
            "scheduled_date": scheduled_date,
            "notes": "Check vital signs",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "pending"
    assert response.json()["created_by"] == "test-user"


def test_list_pending_followups(client):
    future_date = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()

    followup_service.db.collection("followups").document("followup-1").set({
        "followup_id": "followup-1",
        "referral_id": "ref-1",
        "patient_id": "patient-1",
        "scheduled_date": future_date,
        "status": "pending",
    })

    response = client.get("/api/v1/followups/pending")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["status"] == "pending"


def test_list_overdue_followups(client):
    past_date = (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()

    followup_service.db.collection("followups").document("followup-1").set({
        "followup_id": "followup-1",
        "referral_id": "ref-1",
        "patient_id": "patient-1",
        "scheduled_date": past_date,
        "status": "pending",
    })

    response = client.get("/api/v1/followups/overdue")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_record_followup_outcome(client):
    past_date = (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()

    followup_service.db.collection("followups").document("followup-1").set({
        "followup_id": "followup-1",
        "referral_id": "ref-1",
        "patient_id": "patient-1",
        "scheduled_date": past_date,
        "status": "pending",
        "outcome": None,
    })

    response = client.put(
        "/api/v1/followups/followup-1",
        json={
            "status": "completed",
            "outcome": "Patient reviewed by nurse",
            "notes": "All vital signs normal",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert response.json()["outcome"] == "Patient reviewed by nurse"