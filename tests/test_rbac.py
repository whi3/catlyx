import pytest
from fastapi.testclient import TestClient

from core.auth import get_current_user
from main import app
from services import role_service, patient_service
from schemas.role import UserRole


class FakeDocumentSnapshot:
    """Represents a document snapshot with ID and data"""
    def __init__(self, doc_id, data):
        self.id = doc_id
        self._data = data

    @property
    def exists(self):
        return self._data is not None

    def to_dict(self):
        return self._data
    
    def get(self, key, default=None):
        """Get a value from the snapshot data"""
        if self._data is None:
            return default
        return self._data.get(key, default)


class FakeSnapshot:
    def __init__(self, data=None):
        self._data = data

    @property
    def exists(self):
        return self._data is not None

    def to_dict(self):
        return self._data
    
    def get(self, key, default=None):
        """Get a value from the snapshot data"""
        if self._data is None:
            return default
        return self._data.get(key, default)


class FakeDocument:
    def __init__(self, collection, document_id):
        self.collection = collection
        self.document_id = document_id
        self.id = document_id

    def get(self):
        return FakeSnapshot(self.collection.records.get(self.document_id))

    def set(self, data):
        self.collection.records[self.document_id] = dict(data)

    def update(self, data):
        if self.document_id in self.collection.records:
            self.collection.records[self.document_id].update(data)


class FakeCollection:
    def __init__(self):
        self.records = {}
        self._next_id = 0

    def document(self, document_id):
        return FakeDocument(self, document_id)

    def where(self, field, op, value):
        return FakeQuery(self, field, value)

    def order_by(self, field, **kwargs):
        return self

    def limit(self, count):
        return self

    def add(self, data):
        """Add a new document and return (id, ref) tuple"""
        doc_id = f"doc_{self._next_id}"
        self._next_id += 1
        self.records[doc_id] = dict(data)
        return (doc_id, FakeDocument(self, doc_id))

    def stream(self):
        """Return document snapshots with IDs"""
        return [FakeDocumentSnapshot(doc_id, data) for doc_id, data in self.records.items()]


class FakeFirestore:
    def __init__(self):
        self.collections = {}

    def collection(self, name):
        return self.collections.setdefault(name, FakeCollection())


class FakeQuery:
    def __init__(self, collection, field, value):
        self.collection = collection
        self.field = field
        self.value = value

    def order_by(self, field, **kwargs):
        return self

    def limit(self, count):
        return self

    def stream(self):
        return [
            document
            for document in self.collection.stream()
            if document.to_dict().get(self.field) == self.value
        ]


@pytest.fixture
def client(monkeypatch):
    fake_db = FakeFirestore()
    monkeypatch.setattr(role_service, "db", fake_db)
    monkeypatch.setattr(patient_service, "db", fake_db)

    # Pre-populate users with roles
    role_service.db.collection("users").document("admin-user").set({
        "uid": "admin-user",
        "role": UserRole.ADMIN.value,
    })
    role_service.db.collection("users").document("worker-user").set({
        "uid": "worker-user",
        "role": UserRole.CHPS_WORKER.value,
        "facility_id": "clinic-1",
    })

    app.dependency_overrides.clear()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_admin_can_assign_roles(client, monkeypatch):
    app.dependency_overrides[get_current_user] = lambda: {"uid": "admin-user"}

    response = client.post(
        "/api/v1/admin/assign-role",
        json={
            "user_id": "worker-user",
            "role": UserRole.SUPERVISOR.value,
            "facility_id": "clinic-1",
        },
    )

    assert response.status_code == 200


def test_worker_cannot_assign_roles(client, monkeypatch):
    app.dependency_overrides[get_current_user] = lambda: {"uid": "worker-user"}

    response = client.post(
        "/api/v1/admin/assign-role",
        json={
            "user_id": "another-user",
            "role": UserRole.SUPERVISOR.value,
            "facility_id": "clinic-1",
        },
    )

    assert response.status_code == 403


def test_protected_patient_endpoint(client):
    app.dependency_overrides[get_current_user] = lambda: {"uid": "worker-user"}

    response = client.get("/api/v1/patients/")

    assert response.status_code == 200


def test_unprovisioned_user_is_denied(client):
    app.dependency_overrides[get_current_user] = lambda: {"uid": "unknown-user"}
    response = client.get("/api/v1/patients/")
    assert response.status_code == 403


def test_staff_without_facility_is_denied(client):
    role_service.db.collection("users").document("unassigned-user").set({
        "role": UserRole.CHPS_WORKER.value,
    })
    app.dependency_overrides[get_current_user] = lambda: {"uid": "unassigned-user"}
    response = client.get("/api/v1/patients/")
    assert response.status_code == 403


def test_audit_logging(client, monkeypatch):
    app.dependency_overrides[get_current_user] = lambda: {"uid": "admin-user"}

    role_service.log_audit(
        user_id="admin-user",
        endpoint="/api/v1/admin/assign-role",
        method="POST",
        status_code=200,
        details={"assigned_role": "SUPERVISOR"},
    )

    logs = role_service.get_audit_logs(user_id="admin-user", is_admin=True)

    assert len(logs) >= 1
