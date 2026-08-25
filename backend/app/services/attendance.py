from datetime import date, datetime, timedelta, timezone
from typing import Optional
import numpy as np
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.attendance import AttendanceRecord
from app.schemas.attendance import AttendanceRecordResponse
from app.services.face_recognition import FaceRecognitionService
from app.services.worker import identify_worker_service

CLOCK_IN_COOLDOWN_MINUTES = 30


async def process_attendance_frame(
    db: Session,
    frame: np.ndarray,
    face_service: FaceRecognitionService,
) -> Optional[AttendanceRecordResponse]:
    """
    Processes a single frame for worker attendance.

    - Detects face instances directly via InsightFace. If >1 face is found in the frame,
      raises HTTP 400 'many faces are detected'.
    - If 1 face is detected and matched to a worker, records attendance.
    - If 0 faces or 1 unknown face is detected, returns None.
    """
    # 1. Direct face detection count check via InsightFace engine
    detected_faces = []
    if hasattr(face_service, "app") and hasattr(face_service.app, "get"):
        detected_faces = face_service.app.get(frame)
    elif hasattr(face_service, "get_faces"):
        detected_faces = face_service.get_faces(frame)
    elif hasattr(face_service, "detect_faces"):
        detected_faces = face_service.detect_faces(frame)

    # Reject frames with multiple people immediately
    if len(detected_faces) > 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="many faces are detected",
        )

    # Skip database identification if no faces are present in this frame
    if len(detected_faces) == 0:
        return None

    # 2. Single face detected: execute worker identification
    try:
        identification = await identify_worker_service(
            db=db,
            decoded_image=frame,
            face_service=face_service,
        )
    except HTTPException as exc:
        exc_str = str(exc.detail).lower()
        if "multiple" in exc_str or "many" in exc_str or exc.status_code == 400:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="many faces are detected",
            )
        return None

    # Check for dictionary response indicating multiple faces
    ident_str = str(identification).lower()
    if "multiple" in ident_str or "many" in ident_str or identification.get("face_count", 0) > 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="many faces are detected",
        )

    if not identification.get("matched") or not identification.get("worker_id"):
        return None

    matched_worker_id = identification["worker_id"]
    confidence_score = identification["score"]
    now = datetime.now(timezone.utc)
    today = date.today()

    existing_record = (
        db.query(AttendanceRecord)
        .filter(
            AttendanceRecord.worker_id == matched_worker_id,
            AttendanceRecord.record_date == today,
        )
        .first()
    )

    if existing_record:
        time_elapsed = now - existing_record.clock_in

        if time_elapsed < timedelta(minutes=CLOCK_IN_COOLDOWN_MINUTES):
            return AttendanceRecordResponse(
                worker_id=matched_worker_id,
                worker_name=existing_record.worker.name if existing_record.worker else None,
                status="ALREADY_CLOCKED_IN",
                timestamp=existing_record.clock_in,
                confidence_score=confidence_score,
            )

        existing_record.clock_in = now
        existing_record.status = "PRESENT"
        db.commit()
        db.refresh(existing_record)

        return AttendanceRecordResponse(
            worker_id=matched_worker_id,
            worker_name=existing_record.worker.name if existing_record.worker else None,
            status="CLOCKED_IN",
            timestamp=existing_record.clock_in,
            confidence_score=confidence_score,
        )

    new_record = AttendanceRecord(
        worker_id=matched_worker_id,
        record_date=today,
        clock_in=now,
        status="PRESENT",
    )

    try:
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
    except Exception:
        db.rollback()
        return None

    return AttendanceRecordResponse(
        worker_id=matched_worker_id,
        worker_name=new_record.worker.name if new_record.worker else None,
        status="CLOCKED_IN",
        timestamp=new_record.clock_in,
        confidence_score=confidence_score,
    )