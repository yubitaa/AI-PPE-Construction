# import os
# import uuid
# from pathlib import Path

# import cv2
# from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
# from sqlalchemy.orm import Session

# from app.db.dependencies import get_db
# from app.dependencies import get_face_service
# from app.models.video_source import VideoSource
# from app.services.face_recognition import FaceRecognitionService
# from app.services.ppe_monitor import PPEMonitor
# from app.services.worker import identify_worker_service


# router = APIRouter(
#     prefix="/ppe",
#     tags=["PPE Compliance"],
# )


# UPLOAD_DIRECTORY = Path("uploads") / "ppe"


# def _get_video_duration(video_path: str) -> float | None:
#     """
#     Read video duration using OpenCV.

#     Returns duration in seconds when available.
#     """
#     capture = cv2.VideoCapture(video_path)

#     try:
#         if not capture.isOpened():
#             return None

#         fps = capture.get(cv2.CAP_PROP_FPS)
#         frame_count = capture.get(cv2.CAP_PROP_FRAME_COUNT)

#         if fps <= 0 or frame_count <= 0:
#             return None

#         return float(frame_count / fps)

#     finally:
#         capture.release()


# @router.post(
#     "/process-video",
#     status_code=status.HTTP_200_OK,
# )
# async def process_ppe_video(
#     video_file: UploadFile = File(...),
#     frame_skip: int = 5,
#     db: Session = Depends(get_db),
#     face_service: FaceRecognitionService = Depends(get_face_service),
# ):
#     """
#     Process a construction video through the complete Phase 7
#     PPE monitoring pipeline.

#     Pipeline:

#         Video
#           ↓
#         OpenCV
#           ↓
#         YOLO Person/Helmet/Vest
#           ↓
#         ByteTrack
#           ↓
#         Identity cache
#           ↓
#         Face recognition when required
#           ↓
#         PPE association
#           ↓
#         Compliance state tracking
#           ↓
#         PostgreSQL PPE intervals
#     """

#     if frame_skip < 1:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="frame_skip must be at least 1.",
#         )

#     if not video_file.filename:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Video filename is required.",
#         )

#     suffix = Path(video_file.filename).suffix.lower()

#     if not suffix:
#         suffix = ".mp4"

#     allowed_extensions = {
#         ".mp4",
#         ".avi",
#         ".mov",
#         ".mkv",
#         ".webm",
#     }

#     if suffix not in allowed_extensions:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=(
#                 "Unsupported video format. "
#                 "Allowed formats: mp4, avi, mov, mkv, webm."
#             ),
#         )

#     # ------------------------------------------------------------------
#     # 1. Create permanent upload directory
#     # ------------------------------------------------------------------

#     UPLOAD_DIRECTORY.mkdir(
#         parents=True,
#         exist_ok=True,
#     )

#     # Never use the user's filename directly as the stored filename.
#     stored_filename = f"{uuid.uuid4()}{suffix}"

#     video_path = UPLOAD_DIRECTORY / stored_filename

#     # ------------------------------------------------------------------
#     # 2. Save uploaded video
#     # ------------------------------------------------------------------

#     try:
#         with video_path.open("wb") as output_file:
#             while True:
#                 chunk = await video_file.read(1024 * 1024)

#                 if not chunk:
#                     break

#                 output_file.write(chunk)

#     except Exception as exc:
#         if video_path.exists():
#             video_path.unlink()

#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to save uploaded video: {exc}",
#         )

#     # ------------------------------------------------------------------
#     # 3. Verify that OpenCV can open the video
#     # ------------------------------------------------------------------

#     capture = cv2.VideoCapture(str(video_path))

#     try:
#         if not capture.isOpened():
#             if video_path.exists():
#                 video_path.unlink()

#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="The uploaded file is not a readable video.",
#             )
#     finally:
#         capture.release()

#     # ------------------------------------------------------------------
#     # 4. Create VideoSource database record
#     # ------------------------------------------------------------------

#     video_source = VideoSource(
#         file_name=video_file.filename,
#         file_path=str(video_path),
#         duration=_get_video_duration(str(video_path)),
#         status="PROCESSING",
#     )

#     db.add(video_source)
#     db.commit()
#     db.refresh(video_source)

#     # ------------------------------------------------------------------
#     # 5. Identity resolver
#     # ------------------------------------------------------------------

#     async def resolve_identity(person_crop):
#         """
#         Resolve a person crop through the existing Phase 3
#         FaceRecognitionService.

#         UNKNOWN workers return None so the PPE monitor can retry
#         on later frames.

#         Phase 3 recognition logic itself is not modified.
#         """

#         try:
#             result = await identify_worker_service(
#                 db=db,
#                 decoded_image=person_crop,
#                 face_service=face_service,
#             )

#         except HTTPException as exc:
#             # Phase 3 uses 400 for situations such as no face,
#             # multiple faces, etc. For Phase 7 these mean:
#             # "try this track again later."
#             if exc.status_code == status.HTTP_400_BAD_REQUEST:
#                 return None

#             raise

#         worker_id = result.get("worker_id")

#         if not result.get("matched"):
#             return None

#         return worker_id

#     # ------------------------------------------------------------------
#     # 6. Run Phase 7 monitor
#     # ------------------------------------------------------------------

#     monitor = PPEMonitor(
#         db=db,
#         video_id=video_source.video_id,
#         identity_resolver=resolve_identity,
#         frame_skip=frame_skip,
#     )

#     try:
#         result = await monitor.process_source(
#             str(video_path)
#         )

#         # --------------------------------------------------------------
#         # 7. Mark processing as completed
#         # --------------------------------------------------------------

#         video_source.status = "COMPLETED"

#         db.commit()
#         db.refresh(video_source)

#         return {
#             "status": "COMPLETED",
#             "video_id": str(video_source.video_id),
#             "file_name": video_source.file_name,
#             "duration": video_source.duration,
#             "processed_frames": result.processed_frames,
#             "recognized_workers": result.recognized_workers,
#             "unknown_attempts": result.unknown_attempts,
#             "compliance_events": result.compliance_events,
#             "frame_skip": frame_skip,
#         }

#     except HTTPException:
#         video_source.status = "FAILED"
#         db.commit()
#         raise

#     except Exception as exc:
#         db.rollback()

#         try:
#             video_source = (
#                 db.query(VideoSource)
#                 .filter(
#                     VideoSource.video_id
#                     == video_source.video_id
#                 )
#                 .first()
#             )

#             if video_source:
#                 video_source.status = "FAILED"
#                 db.commit()

#         except Exception:
#             db.rollback()

#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"PPE video processing failed: {exc}",
#         )
import os
import uuid
from pathlib import Path

import cv2
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.dependencies import get_face_service
from app.models.video_source import VideoSource
from app.services.face_recognition import FaceRecognitionService
from app.services.ppe_monitor import PPEMonitor
from app.services.worker import identify_worker_service


router = APIRouter(
    prefix="/ppe",
    tags=["PPE Compliance"],
)


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
        # 0.5s interval = fps / 2
        skip = int(round(fps / 2.0))
        return duration, max(1, skip)

    finally:
        capture.release()


@router.post(
    "/process-video",
    status_code=status.HTTP_200_OK,
)
async def process_ppe_video(
    video_file: UploadFile = File(...),
    frame_skip: int | None = None,
    db: Session = Depends(get_db),
    face_service: FaceRecognitionService = Depends(get_face_service),
):
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

    # 3. Read video details & compute 0.5s frame skip
    duration, auto_frame_skip = _get_video_info(str(video_path))
    
    # Use provided frame_skip or default to 0.5s interval
    effective_frame_skip = frame_skip if frame_skip is not None else auto_frame_skip

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
    monitor = PPEMonitor(
        db=db,
        video_id=video_source.video_id,
        identity_resolver=resolve_identity,
        frame_skip=effective_frame_skip,
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