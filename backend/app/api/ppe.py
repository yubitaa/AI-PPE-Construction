import os
import uuid
from datetime import date
from pathlib import Path
from typing import Optional, List  # Added List for response model

import cv2
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status, Query
from sqlalchemy import cast, Date  # Added for date filtering
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.dependencies import get_face_service
from app.models.video_source import VideoSource
from app.models.ppe_log import PPEComplianceLog
from app.schemas.responses import PPEComplianceLogResponse, PPEProcessingResponse
from app.services.face_recognition import FaceRecognitionService
from app.services.ppe_monitor import MonitorConfig, PPEMonitor
from app.services.worker import identify_worker_service

router = APIRouter(tags=["PPE Compliance"])


UPLOAD_DIRECTORY = Path("uploads") / "ppe"


def _get_video_info(video_path: str) -> tuple[float | None, int]:
    """
    Read video duration and calculate frame_skip for 0.5s sampling using OpenCV.

    Returns:
        (duration_in_seconds, frame_skip_for_half_second)
    """
    capture = cv2.VideoCapture(video_path)

    try:
        if not capture.isOpened():
            return None, 15

        fps = capture.get(cv2.CAP_PROP_FPS)
        frame_count = capture.get(cv2.CAP_PROP_FRAME_COUNT)

        if fps <= 0 or frame_count <= 0:
            return None, 15

        duration = float(frame_count / fps)
        # 0.5s interval = fps / 2.0
        skip = int(round(fps / 2.0))
        return duration, max(1, skip)

    finally:
        capture.release()


# ---------------------------------------------------------
# OPERATIONAL APIs (User Side)
# ---------------------------------------------------------

@router.post(
    "/upload",
    response_model=PPEProcessingResponse,
    status_code=status.HTTP_200_OK,
)
async def process_ppe_video(
    video_file: UploadFile = File(...),
    frame_skip: int | None = None,
    db: Session = Depends(get_db),
    face_service: FaceRecognitionService = Depends(get_face_service),
):
    """POST /api/v1/ppe/upload - Processes a video file for PPE Compliance."""
    if not video_file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Video filename is required.",
        )

    suffix = Path(video_file.filename).suffix.lower()
    if not suffix:
        suffix = ".mp4"

    allowed_extensions = {
        ".mp4",
        ".avi",
        ".mov",
        ".mkv",
        ".webm",
    }

    if suffix not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Unsupported video format. "
                "Allowed formats: mp4, avi, mov, mkv, webm."
            ),
        )

    # 1. Create permanent upload directory
    UPLOAD_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    stored_filename = f"{uuid.uuid4()}{suffix}"
    video_path = UPLOAD_DIRECTORY / stored_filename

    # 2. Save uploaded video
    try:
        with video_path.open("wb") as output_file:
            while True:
                chunk = await video_file.read(1024 * 1024)
                if not chunk:
                    break
                output_file.write(chunk)

    except Exception as exc:
        if video_path.exists():
            video_path.unlink()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save uploaded video: {exc}",
        )

    # 3. Read video details and choose the default skip based on the actual FPS
    duration, auto_frame_skip = _get_video_info(str(video_path))
    effective_frame_skip = (
        frame_skip if frame_skip is not None else auto_frame_skip
    )

    if effective_frame_skip < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="frame_skip must be at least 1.",
        )

    # 4. Create VideoSource database record
    video_source = VideoSource(
        file_name=video_file.filename,
        file_path=str(video_path),
        duration=duration,
        status="PROCESSING",
    )

    db.add(video_source)
    db.commit()
    db.refresh(video_source)

    # 5. Identity resolver
    async def resolve_identity(person_crop):
        try:
            result = await identify_worker_service(
                db=db,
                decoded_image=person_crop,
                face_service=face_service,
            )
        except HTTPException as exc:
            if exc.status_code == status.HTTP_400_BAD_REQUEST:
                return None
            raise

        worker_id = result.get("worker_id")
        if not result.get("matched"):
            return None

        return worker_id

    # 6. Run Phase 7 monitor
    config = MonitorConfig(
        frame_skip=effective_frame_skip,
        temporal_confirmations=5,
    )

    monitor = PPEMonitor(
        db=db,
        video_id=video_source.video_id,
        identity_resolver=resolve_identity,
        config=config,
    )

    try:
        result = await monitor.process_source(str(video_path))

        video_source.status = "COMPLETED"
        db.commit()
        db.refresh(video_source)

        return {
            "status": "COMPLETED",
            "video_id": str(video_source.video_id),
            "file_name": video_source.file_name,
            "duration": video_source.duration,
            "processed_frames": result.processed_frames,
            "recognized_workers": result.recognized_workers,
            "unknown_attempts": result.unknown_attempts,
            "compliance_events": result.compliance_events,
            "frame_skip": effective_frame_skip,
        }

    except HTTPException:
        video_source.status = "FAILED"
        db.commit()
        raise

    except Exception as exc:
        db.rollback()
        try:
            video_source = (
                db.query(VideoSource)
                .filter(VideoSource.video_id == video_source.video_id)
                .first()
            )
            if video_source:
                video_source.status = "FAILED"
                db.commit()
        except Exception:
            db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PPE video processing failed: {exc}",
        )


# ---------------------------------------------------------
# QUERY APIs (Admin Side)
# ---------------------------------------------------------

@router.get(
    "/results",
    response_model=List[PPEComplianceLogResponse],  # Added contract
    status_code=status.HTTP_200_OK
)
def get_ppe_results(
    query_date: Optional[date] = Query(None, alias="date"),
    worker_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    GET /api/v1/ppe/results
    Fetches PPE compliance logs filtered by worker_id and/or calendar date.
    """
    query = db.query(PPEComplianceLog)

    # FIXED: Date filtering by joining VideoSource (Matches Phase 8 Logic)
    if query_date:
        query = query.join(VideoSource, PPEComplianceLog.video_id == VideoSource.video_id)
        query = query.filter(cast(VideoSource.uploaded_at, Date) == query_date)

    if worker_id:
        query = query.filter(PPEComplianceLog.worker_id == worker_id)

    return query.all()