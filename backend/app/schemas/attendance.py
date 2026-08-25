#Pydantic schemas define the strict data contract between your FastAPI backend and API clients (such as frontends or mobile apps).
#  app/schemas/attendance.py
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class AttendanceRecordResponse(BaseModel):
    """
    Represents the result of an individual attendance clock-in attempt for a single worker.
    """
    model_config = ConfigDict(from_attributes=True)

    worker_id: UUID = Field(..., description="Database primary key UUID of the recognized worker")
    worker_name: Optional[str] = Field(None, description="Full name of the worker")
    status: str = Field(..., description="Clock-in state: 'CLOCKED_IN' or 'ALREADY_CLOCKED_IN'")
    timestamp: datetime = Field(..., description="Exact date and time when the clock-in was recorded")
    confidence_score: float = Field(..., description="Face resemblance match accuracy percentage (0-100%)")


class VideoAttendanceResult(BaseModel):
    """
    Represents the aggregate response summary returned after processing a full video file or camera stream.
    """
    total_frames_processed: int = Field(..., description="Total number of video frames extracted and analyzed")
    faces_detected: int = Field(..., description="Total count of face instances identified across frames")
    records_created: List[AttendanceRecordResponse] = Field(..., description="Unique clock-in records generated or verified")
    unknown_faces_count: int = Field(..., description="Count of detected faces that fell below recognition threshold")