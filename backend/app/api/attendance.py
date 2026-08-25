import os
import tempfile
from typing import Dict
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.dependencies import get_face_service
from app.schemas.attendance import (
    AttendanceRecordResponse,
    VideoAttendanceResult,
)
from app.services.attendance import process_attendance_frame
from app.services.face_recognition import FaceRecognitionService
from app.services.worker import change_image_to_ndarray
from app.vision.frame_extractor import extract_frames

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.post(
    "/process-frame",
    response_model=AttendanceRecordResponse,
    status_code=status.HTTP_200_OK,
)
async def process_single_frame_attendance(
    face_image: UploadFile = File(...),
    db: Session = Depends(get_db),
    face_service: FaceRecognitionService = Depends(get_face_service),
):
    """
    Decodes single frame image:
    - 400 Bad Request: 'many faces are detected' if >1 faces are present.
    - 404 Not Found: If single face is unknown or no face exists.
    - 200 OK: If 1 face is successfully identified.
    """
    decoded_image = change_image_to_ndarray(face_image)
    record = await process_attendance_frame(
        db=db,
        frame=decoded_image,
        face_service=face_service,
    )

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No recognized worker found in frame or resemblance score below threshold.",
        )

    return record


@router.post(
    "/process-video",
    response_model=VideoAttendanceResult,
    status_code=status.HTTP_200_OK,
)
async def process_video_attendance(
    video_file: UploadFile = File(...),
    frame_skip: int = 5,
    db: Session = Depends(get_db),
    face_service: FaceRecognitionService = Depends(get_face_service),
):
    """
    Processes video stream:
    - Returns 400 Bad Request 'many faces are detected' if multiple faces appear in any frame.
    - Returns 200 OK and stops loop as soon as 1 single worker face is matched.
    """
    suffix = os.path.splitext(video_file.filename)[1] or ".mp4"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await video_file.read()
        tmp.write(content)
        tmp_path = tmp.name

    total_frames = 0
    faces_detected = 0
    unknown_faces = 0
    processed_records: Dict[str, AttendanceRecordResponse] = {}

    try:
        for frame in extract_frames(tmp_path, frame_skip=frame_skip):
            total_frames += 1
            record = await process_attendance_frame(
                db=db,
                frame=frame,
                face_service=face_service,
            )

            if record:
                faces_detected += 1
                worker_key = str(record.worker_id)
                processed_records[worker_key] = record

                # Stop extracting frames once 1 worker is clocked in
                break
            else:
                unknown_faces += 1

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    return VideoAttendanceResult(
        total_frames_processed=total_frames,
        faces_detected=faces_detected,
        records_created=list(processed_records.values()),
        unknown_faces_count=unknown_faces,
    )