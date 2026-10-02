from typing import Any, List
from pydantic import BaseModel, Field

class SyncRequest(BaseModel):
    last_synced_at: str
    patient_change: list[dict[str, Any]] = Field(default_factory=list)

class SyncResponse(BaseModel):
    synced_at: str
    patients: List[dict]
    sync_results: List[dict] = Field(default_factory=list)
    conflicts: list[dict] = Field(default_factory=list)