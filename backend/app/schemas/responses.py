from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

# 1. Worker Response Contract
class WorkerResponse(BaseModel):
    worker_id: UUID
    name: str
    employee_id: str
    role: str
    department: str
    tag_id: Optional[str] = None
    is_active: bool  # <--- NEW: Tells the frontend if they are active or soft-deleted
    
    model_config = ConfigDict(from_attributes=True)

# 2. PPE Log Response Contract
class PPEComplianceLogResponse(BaseModel):
    log_id: UUID
    worker_id: UUID
    video_id: UUID
    start_timestamp: float
    end_timestamp: Optional[float] = None
    helmet_detected: bool
    vest_detected: bool
    compliance_status: str
    
    model_config = ConfigDict(from_attributes=True)

# 3. Daily Report Response Contract
class DailyReportResponse(BaseModel):
    report_id: UUID
    report_date: date
    generated_at: datetime
    attendance_summary: dict
    ppe_summary: dict
    compliance_rate: float
    report_content: str
    
    model_config = ConfigDict(from_attributes=True)

# 4. Camera Clock-in Response Contract
class CameraClockInResponse(BaseModel):
    status: str
    worker_id: Optional[str] = None
    worker_name: Optional[str] = None
    timestamp: Optional[datetime] = None
    next_allowed_clock_in: Optional[datetime] = None


# 5. PPE Processing Response Contract
class PPEProcessingResponse(BaseModel):
    status: str
    video_id: UUID
    file_name: str
    duration: Optional[float] = None  # <--- THE FIX
    processed_frames: int
    recognized_workers: int
    unknown_attempts: int
    compliance_events: int
    frame_skip: int