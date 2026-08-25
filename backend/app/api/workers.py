from typing import List, Optional

import numpy as np
from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.dependencies import get_face_service  # [MODIFIED] Imported from app.dependencies instead of app.main
from app.schemas.worker import (
    WorkerIdentificationResponse,
    WorkerRegistrationResponse,
)
from app.services.face_recognition import FaceRecognitionService
from app.services.worker import (
    change_image_to_ndarray,
    identify_worker_service,
    register_worker_service,
)

router = APIRouter(prefix="/workers", tags=["Workers"])


@router.post(
    "/register",
    response_model=WorkerRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_worker(
    name: str = Form(...),
    employee_id: str = Form(...),
    role: str = Form(...),
    department: str = Form(...),
    tag_id: Optional[str] = Form(None),
    face_images: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
    face_service: FaceRecognitionService = Depends(get_face_service),
):
    """Registers a new worker and processes their face embeddings."""
    worker = await register_worker_service(
        db=db,
        name=name,
        employee_id=employee_id,
        role=role,
        department=department,
        tag_id=tag_id,
        face_images=face_images,
        face_service=face_service,
    )

    return {"worker_id": worker.worker_id, "status": "registered"}


@router.post(
    "/identify",
    response_model=WorkerIdentificationResponse,
    status_code=status.HTTP_200_OK,
)
async def identify_worker(
    face_image: UploadFile = File(...),
    db: Session = Depends(get_db),
    face_service: FaceRecognitionService = Depends(get_face_service),
):
    """Step 11: Endpoint to process a single frame/image for face recognition."""
    decoded_image = change_image_to_ndarray(face_image)
    return await identify_worker_service(
        db=db,
        decoded_image=decoded_image,
        face_service=face_service,
    )