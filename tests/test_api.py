import pytest
import asyncio
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient

from core.auth import get_current_user
from main import app
from services import (
    followup_service,
    notification_service,
    patient_service,
    referral_service,
    risk_service,
    role_service,
    push_service,
)
from schemas.role import UserRole


class FakeSnapshot:
    def __init__(self, data=None, document_id=None):
        self._data = data
        self.id = document_id

    @property
    def exists(self):
        return self._data is not None

    def to_dict(self):
        return self._data


class FakeDocument:
    def __init__(self, collection, document_id):
        self.collection = collection
        self.document_id = document_id
        self.id = document_id

    def get(self):
        return FakeSnapshot(
            self.collection.records.get(self.document_id),
            document_id=self.document_id,
        )

    def set(self, data):
        self.collection.records[self.document_id] = dict(data)

    def update(self, data):
        self.collection.records[self.document_id].update(data)


class FakeCollection:
    def __init__(self):
        self.records = {}
        self._next_id = 0

    def document(self, document_id):
        return FakeDocument(self, document_id)

    def stream(self):
        return [FakeSnapshot(data) for data in self.records.values()]

    def where(self, field, operator, value):
        return FakeQuery(self, field, value)

    def add(self, data):
        document_id = f"audit-{self._next_id}"
        self._next_id += 1
        self.records[document_id] = dict(data)
        return document_id, FakeDocument(self, document_id)


class FakeQuery:
    def __init__(self, collection, field, value):
        self.collection = collection
        self.filters = [(field, "==", value)]
        self.cursor_id = None
        self.limit_count = None

    def where(self, field, operator, value):
        self.filters.append((field, operator, value))
        return self

    def start_after(self, snapshot):
        self.cursor_id = snapshot.id
        return self

    def stream(self):
        matching = [
            FakeSnapshot(data, document_id)
            for document_id, data in self.collection.records.items()
            if all(
                data.get(field) == value
                if operator == "=="
                else data.get(field) is not None and data.get(field) <= value
                for field, operator, value in self.filters
            )
        ]
        if self.cursor_id:
            cursor_index = next(
                (index for index, document in enumerate(matching) if document.id == self.cursor_id),
                -1,
            )
            matching = matching[cursor_index + 1:]
        if self.limit_count is not None:
            matching = matching[:self.limit_count]
        return matching

    def order_by(self, *args, **kwargs):
        return self

    def limit(self, count):
        self.limit_count = count
        return self


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
    monkeypatch.setattr(followup_service, "db", fake_db)
    monkeypatch.setattr(notification_service, "db", fake_db)
    monkeypatch.setattr(push_service, "db", fake_db)
    monkeypatch.setattr(role_service, "db", fake_db)
    fake_db.collection("users").document("test-user").set({
        "role": UserRole.CHPS_WORKER.value,
        "facility_id": "clinic-1",
    })
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

    assert response.status_code in {401, 503}


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

    assert create_response.status_code == 201
    patient_id = create_response.json()["patient_id"]

    get_response = client.get(f"/api/v1/patients/{patient_id}")

    assert get_response.status_code == 200
    assert get_response.json()["patient_type"] == "mother"
    assert get_response.json()["first_name"] == "Ama"


def test_registration_rejects_implausible_values(client):
    response = client.post(
        "/api/v1/patients/children",
        json={
            "first_name": "Kofi",
            "last_name": "Mensah",
            "age_months": 90,
            "guardian_name": "Ama Mensah",
            "community": "Kumasi",
            "weight": 12,
        },
    )
    assert response.status_code == 422


def test_patient_records_are_facility_scoped(client):
    patient_service.db.collection("patients").document("other-clinic-patient").set({
        "patient_id": "other-clinic-patient",
        "patient_type": "mother",
        "facility_id": "clinic-2",
    })
    response = client.get("/api/v1/patients/other-clinic-patient")
    assert response.status_code == 404


def test_risk_assessment_escalates_severe_bleeding(client):
    patient_id = "mother-1"
    patient_service.db.collection("patients").document(patient_id).set(
        {"patient_id": patient_id, "patient_type": "mother", "facility_id": "clinic-1"}
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
    assert response.json()["risk_level"] == "High Risk"
    assert response.json()["risk_score"] == 4
    assert response.json()["assessed_by"] == "test-user"
    assert response.json()["recommendation"] == "Seek urgent clinical assessment or referral now."
    assert response.json()["clinical_validation_status"] == "pending"
    assert response.json()["decision_support_only"] is True


def test_child_convulsions_escalate_to_urgent_review(client):
    patient_id = "child-1"
    patient_service.db.collection("patients").document(patient_id).set({
        "patient_id": patient_id,
        "patient_type": "child",
        "age_months": 12,
        "facility_id": "clinic-1",
    })
    response = client.post(
        "/api/v1/risk-assessment/",
        json={"patient_id": patient_id, "convulsions": True},
    )
    assert response.status_code == 200
    assert response.json()["risk_level"] == "High Risk"
    assert response.json()["recommendation"] == "Seek urgent clinical assessment or referral now."


def test_risk_assessment_rejects_empty_screening(client):
    patient_id = "empty-screening-mother"
    patient_service.db.collection("patients").document(patient_id).set({
        "patient_id": patient_id,
        "patient_type": "mother",
        "pregnancy_weeks": 24,
        "facility_id": "clinic-1",
    })
    response = client.post(
        "/api/v1/risk-assessment/",
        json={"patient_id": patient_id},
    )
    assert response.status_code == 422


def test_risk_assessment_is_disabled_without_clinical_approval(client, monkeypatch):
    from config import settings

    patient_service.db.collection("patients").document("approval-gate-patient").set({
        "patient_id": "approval-gate-patient",
        "patient_type": "mother",
        "pregnancy_weeks": 24,
        "facility_id": "clinic-1",
    })
    monkeypatch.setattr(settings, "RISK_RULES_CLINICALLY_APPROVED", False)
    response = client.post(
        "/api/v1/risk-assessment/",
        json={"patient_id": "approval-gate-patient", "severe_bleeding": True},
    )
    assert response.status_code == 503


def test_failed_sms_is_queued_for_retry(client, monkeypatch):
    import config

    async def fail_delivery(phone_number, message):
        return False

    monkeypatch.setattr(config.settings, "SMS_ENABLED", True)
    monkeypatch.setattr(notification_service, "send_sms", fail_delivery)
    result = asyncio.run(notification_service.dispatch_referral_sms(
        patient_id="patient-1",
        referral_id="referral-1",
        phone_number="0240000000",
        message="Referral created",
    ))
    records = notification_service.db.collection("notifications").records
    item = next(iter(records.values()))
    assert result == "pending"
    assert item["attempt_count"] == 1
    assert item["status"] == "pending"
    assert item["next_attempt_at"] > datetime.now(timezone.utc).isoformat()
    notification_service.db.collection("notifications").document(
        item["notification_id"]
    ).update({"next_attempt_at": (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()})

    async def succeed_delivery(phone_number, message):
        return True

    monkeypatch.setattr(notification_service, "send_sms", succeed_delivery)
    retry_result = asyncio.run(notification_service.retry_due_notifications())
    assert retry_result == {"processed": 1, "sent": 1, "failed": 0}
    assert item["status"] == "sent"
    assert item["attempt_count"] == 2


def test_assessment_history_uses_a_cursor(client):
    patient_id = "history-patient"
    patient_service.db.collection("patients").document(patient_id).set({
        "patient_id": patient_id,
        "patient_type": "mother",
        "facility_id": "clinic-1",
    })
    assessments = patient_service.db.collection("risk_assessments")
    for index, assessed_at in enumerate((
        "2026-10-03T03:00:00+00:00",
        "2026-10-03T02:00:00+00:00",
        "2026-10-03T01:00:00+00:00",
    )):
        assessments.document(f"assessment-{index}").set({
            "assessment_id": f"assessment-{index}",
            "patient_id": patient_id,
            "assessed_at": assessed_at,
            "risk_level": "High Risk",
        })

    first_page = client.get(f"/api/v1/patients/{patient_id}/assessments?limit=2")
    assert first_page.status_code == 200
    assert len(first_page.json()) == 2
    cursor = first_page.headers["X-Next-Cursor"]

    second_page = client.get(
        f"/api/v1/patients/{patient_id}/assessments?limit=2&cursor={cursor}"
    )
    assert second_page.status_code == 200
    assert len(second_page.json()) == 1


def test_referral_status_and_follow_up_workflow(client):
    patient_id = "patient-1"
    patient_service.db.collection("patients").document(patient_id).set(
        {"patient_id": patient_id, "patient_type": "child", "facility_id": "clinic-1"}
    )

    response = client.post(
        "/api/v1/referrals/",
        json={
            "patient_id": patient_id,
            "reason": "Needs clinical review",
            "destination": "District hospital",
        },
    )

    assert response.status_code == 201
    referral_id = response.json()["referral_id"]
    assert response.json()["status"] == "pending"

    scheduled_date = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    follow_up_response = client.post(
        "/api/v1/followups/",
        json={
            "referral_id": referral_id,
            "patient_id": patient_id,
            "scheduled_date": scheduled_date,
            "notes": "Review by nurse",
        },
    )
    followup_id = follow_up_response.json()["followup_id"]
    closeout_response = client.put(
        f"/api/v1/followups/{followup_id}",
        json={"status": "completed", "outcome": "Reviewed by nurse"},
    )
    status_response = client.put(
        f"/api/v1/referrals/{referral_id}/status",
        json={"status": "completed"},
    )

    assert status_response.status_code == 200
    assert status_response.json()["status"] == "completed"
    assert follow_up_response.status_code == 201
    assert closeout_response.status_code == 200
    assert closeout_response.json()["status"] == "completed"
