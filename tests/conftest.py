import sys
from pathlib import Path
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class _Snapshot:
    def __init__(self, data=None, document_id=None):
        self._data = data
        self.id = document_id
        self.exists = data is not None

    def to_dict(self):
        return self._data


class _Document:
    def __init__(self, collection, document_id):
        self.collection = collection
        self.id = document_id

    def get(self):
        return _Snapshot(self.collection.records.get(self.id), self.id)

    def update(self, values):
        self.collection.records[self.id].update(values)


class _Collection:
    def __init__(self):
        self.records = {}
        self.next_id = 0

    def document(self, document_id):
        return _Document(self, document_id)

    def add(self, data):
        document_id = f"audit-{self.next_id}"
        self.next_id += 1
        self.records[document_id] = dict(data)
        return document_id, _Document(self, document_id)


class _Database:
    def __init__(self):
        self.collections = {}

    def collection(self, name):
        return self.collections.setdefault(name, _Collection())


@pytest.fixture(autouse=True)
def isolate_audit_database(monkeypatch):
    """Keep the HTTP audit middleware away from any configured Firebase project."""
    from services import role_service

    monkeypatch.setattr(role_service, "db", _Database())
