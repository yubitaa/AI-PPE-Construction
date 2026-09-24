from typing import List, Optional

import numpy as np
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError  # Added for safe deletion

from app.db.dependencies import get_db
from app.dependencies import get_face_service
from app.models.worker import Worker
from app.models.attendance import AttendanceRecord  # <--- Add this
from app.models.ppe_log import PPEComplianceLog
from app.schemas.worker import (
    WorkerIdentificationResponse,
    WorkerRegistrationResponse,
)
from app.schemas.responses import WorkerResponse  # Added strict response contract
from app.services.face_recognition import FaceRecognitionService
from app.services.worker import (
    change_image_to_ndarray,
    identify_worker_service,
    register_worker_service,
)

router = APIRouter(tags=["Workers"])

# UPDATED SCHEMA: Admin can now update all editable fields
class WorkerUpdateSchema(BaseModel):
    name: Optional[str] = None
    employee_id: Optional[str] = None
    role: Optional[str] = None
    department: Optional[str] = None
    tag_id: Optional[str] = None


@router.post(
    "",
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


# ---------------------------------------------------------
# NEW PHASE 10 CRUD ENDPOINTS (Admin Side)
# ---------------------------------------------------------

@router.get("", response_model=List[WorkerResponse])
def list_workers(db: Session = Depends(get_db)):
    """GET /api/v1/workers - Lists all active workers."""
    # FIXED: Only returns workers where is_active is True
    workers = db.query(Worker).filter(Worker.is_active == True).all()
    return workers


@router.get("/{worker_id}", response_model=WorkerResponse)
def get_worker(worker_id: str, db: Session = Depends(get_db)):
    """GET /api/v1/workers/{worker_id} - Gets details for a specific worker."""
    worker = db.query(Worker).filter(Worker.worker_id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail=f"Worker with ID {worker_id} not found.")
    return worker


@router.put("/{worker_id}", response_model=WorkerResponse)
def update_worker(worker_id: str, update_data: WorkerUpdateSchema, db: Session = Depends(get_db)):
    """PUT /api/v1/workers/{worker_id} - Updates a worker's profile."""
    worker = db.query(Worker).filter(Worker.worker_id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail=f"Worker with ID {worker_id} not found.")
    
    # FIXED: exclude_none=True prevents overwriting fields with null
    update_dict = update_data.model_dump(exclude_unset=True, exclude_none=True)
    for key, value in update_dict.items():
        setattr(worker, key, value)
        
    try:
        db.commit()
        db.refresh(worker)
        return worker
    except IntegrityError:
        # FIXED: Handles duplicate employee_ids or database conflicts
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Worker update conflicts with existing database data (e.g., duplicate employee_id)."
        )

@router.delete("/{worker_id}")
def delete_worker(worker_id: str, db: Session = Depends(get_db)):
    """DELETE /api/v1/workers/{worker_id} - Smart Delete (Explicit Check)."""
    worker = db.query(Worker).filter(Worker.worker_id == worker_id).first()
    
    if not worker:
        raise HTTPException(status_code=404, detail=f"Worker with ID {worker_id} not found.")

    # 1. Explicitly check if the worker has any historical attendance or PPE records
    attendance_count = db.query(AttendanceRecord).filter(AttendanceRecord.worker_id == worker_id).count()
    ppe_count = db.query(PPEComplianceLog).filter(PPEComplianceLog.worker_id == worker_id).count()

    # 2. Decide the deletion method based on the counts
    if attendance_count == 0 and ppe_count == 0:
        # No history -> Safe to Hard Delete (Face embeddings will cascade delete)
        db.delete(worker)
        db.commit()
        return {"worker_id": worker_id, "deleted": True, "method": "hard_delete"}
    
    else:
        # Has history -> Protect the data with a Soft Delete
        worker.is_active = False
        db.commit()
        return {"worker_id": worker_id, "deleted": True, "method": "soft_delete"}
# ---------------------------------------------------------
# RETAINED IDENTIFY ENDPOINT
# ---------------------------------------------------------

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