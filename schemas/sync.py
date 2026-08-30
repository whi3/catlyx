from typing import List
from pydantic import BaseModel

class SyncRequest(BaseModel):
    last_synced_at: str

class SyncResponse(BaseModel):
    synced_at: str
    patients: List[dict]