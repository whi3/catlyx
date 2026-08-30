import pytest
from fastapi.testclient import TestClient

from core.auth import get_current_user
from main import app
from services import patient_service, referral_service, risk_service


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
        self.collection.records[self.document_id].update(data)


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
    monkeypatch.setattr(patient_service, "db", fake_db)
    monkeypatch.setattr(risk_service, "db", fake_db)
    monkeypatch.setattr(referral_service, "db", fake_db)
    app.dependency_overrides[get_current_user] = lambda: {"uid": "test-user"}

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_root_and_health(client):
    assert client.get("/").status_code == 200
    response = client.get("/health/")

    assert response.status_code == 200
    assert response.json()["status"] == "I'm good"


def test_protected_patient_endpoint_requires_authentication():
    with TestClient(app) as unauthenticated_client:
        response = unauthenticated_client.post(
            "/api/v1/patients/mothers",
            json={"first_name": "Ama", "last_name": "Mensah"},
        )

    assert response.status_code == 401


def test_register_and_retrieve_mother(client):
    payload = {
        "first_name": "Ama",
        "last_name": "Mensah",
        "age": 27,
        "phone_number": "0240000000",
        "community": "Kumasi",
        "pregnancy_weeks": 24,
    }

    create_response = client.post("/api/v1/patients/mothers", json=payload)

    assert create_response.status_code == 200
    patient_id = create_response.json()["patient_id"]

    get_response = client.get(f"/api/v1/patients/{patient_id}")

    assert get_response.status_code == 200
    assert get_response.json()["patient_type"] == "mother"
    assert get_response.json()["first_name"] == "Ama"


def test_risk_assessment_records_moderate_risk_for_severe_bleeding(client):
    patient_id = "mother-1"
    patient_service.db.collection("patients").document(patient_id).set(
        {"patient_id": patient_id, "patient_type": "mother"}
    )

    response = client.post(
        "/api/v1/risk-assessment/",
        json={
            "patient_id": patient_id,
            "age": 27,
            "pregnancy_weeks": 24,
            "temperature": 37,
            "weight": 65,
            "severe_bleeding": True,
        },
    )

    assert response.status_code == 200
    assert response.json()["risk_level"] == "Moderate Risk"
    assert response.json()["risk_score"] == 4
    assert response.json()["assessed_by"] == "test-user"


def test_referral_status_and_follow_up_workflow(client):
    patient_id = "patient-1"
    patient_service.db.collection("patients").document(patient_id).set(
        {"patient_id": patient_id, "patient_type": "child"}
    )

    response = client.post(
        "/api/v1/referrals/",
        json={
            "patient_id": patient_id,
            "reason": "Needs clinical review",
            "destination": "District hospital",
        },
    )

    assert response.status_code == 200
    referral_id = response.json()["referral_id"]
    assert response.json()["status"] == "pending"

    status_response = client.put(
        f"/api/v1/referrals/{referral_id}/status",
        json={"status": "completed"},
    )
    follow_up_response = client.post(
        f"/api/v1/referrals/{referral_id}/follow-up",
        json={"notes": "Reviewed by nurse", "completed": True},
    )

    assert status_response.status_code == 200
    assert status_response.json()["status"] == "completed"
    assert follow_up_response.status_code == 200
    assert follow_up_response.json()["follow_up_completed"] is True