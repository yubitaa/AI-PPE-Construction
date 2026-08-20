from fastapi import APIRouter, Depends, Form, File, UploadFile, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.dependencies import get_db
from app.schemas.worker import WorkerRegistrationResponse, WorkerIdentificationResponse
from app.services.worker import register_worker_service, identify_worker_service

router = APIRouter(prefix="/workers", tags=["Workers"])

@router.post(
    "/register", 
    response_model=WorkerRegistrationResponse, 
    status_code=status.HTTP_201_CREATED
)
async def register_worker(
    name: str = Form(...),
    employee_id: str = Form(...),
    role: str = Form(...),
    department: str = Form(...),
    tag_id: Optional[str] = Form(None),
    face_images: list[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Registers a new worker and processes their face embeddings.
    """
    # The service handles the transactional logic and image count validation
    worker = await register_worker_service(
        db=db,
        name=name,
        employee_id=employee_id,
        role=role,
        department=department,
        tag_id=tag_id,
        face_images=face_images
    )
    
    # Return the explicit dictionary that matches the Pydantic response schema
    return {
        "worker_id": worker.worker_id,
        "status": "registered"
    }

@router.post(
    "/identify",
    response_model=WorkerIdentificationResponse,
    status_code=status.HTTP_200_OK
)
async def identify_worker(
    face_image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Step 11: Endpoint to process a single frame/image for face recognition.
    """
    return await identify_worker_service(db, face_image)