import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict

class WorkerRegistrationResponse(BaseModel):
    """
    API response contract for successful worker registration.
    """
    worker_id: uuid.UUID
    status: str

    # This configuration allows Pydantic to extract the 'worker_id' 
    # directly from the SQLAlchemy Worker model instance.
    model_config = ConfigDict(from_attributes=True)
    
class WorkerIdentificationResponse(BaseModel):
    """
    API response contract for worker identification.
    Returns the worker ID if matched, or null if UNKNOWN.
    """
    worker_id: Optional[uuid.UUID]
    score: float
    matched: bool