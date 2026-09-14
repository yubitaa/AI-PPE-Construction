import os
import tempfile
from datetime import date, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status, Query
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.dependencies import get_face_service
from app.models.attendance import AttendanceRecord
from app.schemas.attendance import AttendanceRecordResponse
from app.schemas.responses import CameraClockInResponse  # Added strict response contract
from app.services.attendance import (
    CLOCK_IN_COOLDOWN_MINUTES,
    process_attendance_frame,
)
from app.services.face_recognition import FaceRecognitionService
from app.services.worker import change_image_to_ndarray
from app.vision.frame_extractor import extract_frames

router = APIRouter(tags=["Attendance"])


# ---------------------------------------------------------
# OPERATIONAL APIs (User Side)
# ---------------------------------------------------------

@router.post(
    "/upload",
    response_model=AttendanceRecordResponse,
    status_code=status.HTTP_200_OK,
)
async def upload_clockin_video(
    video_file: UploadFile = File(...),
    frame_skip: int = 5,
    db: Session = Depends(get_db),
    face_service: FaceRecognitionService = Depends(get_face_service),
):
    """POST /api/v1/attendance/upload - Processes a video file for clock-in."""
    suffix = os.path.splitext(video_file.filename)[1] or ".mp4"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await video_file.read()
        tmp.write(content)
        tmp_path = tmp.name

    final_record = None

    try:
        for frame in extract_frames(tmp_path, frame_skip=frame_skip):
            record = await process_attendance_frame(
                db=db,
                frame=frame,
                face_service=face_service,
            )

            if record:
                final_record = record
                break  # Stop extracting frames once 1 worker is clocked in

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    if not final_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No recognized worker found in the video."
        )

    return final_record


@router.post(
    "/camera-clockin",
    response_model=CameraClockInResponse,  # Added contract
    status_code=status.HTTP_200_OK,
)
async def camera_clockin(
    frame: UploadFile = File(...),
    db: Session = Depends(get_db),
    face_service: FaceRecognitionService = Depends(get_face_service),
):
    """
    POST /api/v1/attendance/camera-clockin
    Processes a temporary camera frame for real-time clock-in.
    
    FRONTEND WORKFLOW (POLLING):
    - "UNKNOWN": No confirmed worker identified yet. The frontend MUST keep 
                 sending frames (do not stop the camera).
    - "CLOCKED_IN": Success. Stop the camera.
    - "ALREADY_CLOCKED_IN": Worker recognized but already clocked in today. Stop camera.
    """
    decoded_image = change_image_to_ndarray(frame)
    
    try:
        record = await process_attendance_frame(
            db=db,
            frame=decoded_image,
            face_service=face_service,
        )

        if not record:
            return {"status": "UNKNOWN", "worker_id": None}

        next_allowed_clock_in = None
        if record.timestamp:
            next_allowed_clock_in = record.timestamp + timedelta(minutes=30)

        return {
            "status": record.status,
            "worker_id": str(record.worker_id),
            "worker_name": record.worker_name,
            "timestamp": record.timestamp,
            "next_allowed_clock_in": next_allowed_clock_in,
        }

    except HTTPException as e:
        # FIXED: Precise string matching to prevent false positives
        if "already clocked in" in str(e.detail).lower():
            return {"status": "ALREADY_CLOCKED_IN", "worker_id": None}
        raise e


# ---------------------------------------------------------
# QUERY APIs (Admin Side)
# ---------------------------------------------------------

@router.get(
    "",
    response_model=List[AttendanceRecordResponse],
    status_code=status.HTTP_200_OK
)
def get_attendance_results(
    query_date: Optional[date] = Query(None, alias="date"),
    worker_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    GET /api/v1/attendance
    Fetches attendance results filtered by date and/or worker_id.
    """
    query = db.query(AttendanceRecord)

    if query_date:
        query = query.filter(AttendanceRecord.record_date == query_date)
    
    if worker_id:
        query = query.filter(AttendanceRecord.worker_id == worker_id)


    records = query.all()

    return [
        {
            "worker_id": record.worker_id,
            "worker_name": record.worker.name if record.worker else None,
            "status": (
                "CLOCKED_IN"
                if record.status == "PRESENT"
                else record.status
            ),
            "timestamp": record.clock_in,
            "clock_out": record.clock_in + timedelta(
                minutes=CLOCK_IN_COOLDOWN_MINUTES
            ),
            # Historical attendance rows do not persist recognition confidence.
            "confidence_score": None,
        }
        for record in records
    ]