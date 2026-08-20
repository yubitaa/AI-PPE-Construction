from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException, status
from typing import List, Optional
from sqlalchemy import asc
import logging

from app.models.worker import Worker
from app.models.face_embedding import FaceEmbedding
from app.services.face_recognition import generate_embedding

# Constants explicitly marked as development/temporary values
EXPECTED_EMBEDDING_DIMENSION = 512
DEV_RECOGNITION_THRESHOLD = 1.2

async def register_worker_service(
    db: Session,
    name: str,
    employee_id: str,
    role: str,
    department: str,
    tag_id: Optional[str],
    face_images: List[UploadFile]
) -> Worker:
    
    # NEW: 0. Basic Metadata Validation
    if not name.strip() or not employee_id.strip() or not role.strip() or not department.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Metadata fields (name, employee_id, role, department) cannot be empty."
        )
    if tag_id is not None and not tag_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="tag_id cannot be empty if provided."
        )

    # 1. Validate image count boundary
    if not (3 <= len(face_images) <= 5):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration requires between 3 and 5 face images."
        )

    # 2. Application-level duplicate checks
    if db.query(Worker).filter(Worker.employee_id == employee_id).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Worker with employee ID '{employee_id}' already exists."
        )
    if tag_id and db.query(Worker).filter(Worker.tag_id == tag_id).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Worker with tag ID '{tag_id}' already exists."
        )

    # 3. Process ALL images first before modifying the database
    embeddings = []
    for index, image in enumerate(face_images):
        image_bytes = await image.read()
        result = generate_embedding(image_bytes)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Face recognition failed on image {index + 1}: {result.get('error')}"
            )
            
        vector = result["embedding"]
        
        # 4. Explicit dimension validation
        if len(vector) != EXPECTED_EMBEDDING_DIMENSION:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Model returned invalid embedding dimension. Expected {EXPECTED_EMBEDDING_DIMENSION}, got {len(vector)}."
            )
            
        embeddings.append(vector)

    # 5. Database transaction with explicit rollback
    try:
        new_worker = Worker(
            name=name,
            employee_id=employee_id,
            role=role,
            department=department,
            tag_id=tag_id
        )
        
        db.add(new_worker)
        db.flush() 

        for embedding_vector in embeddings:
            new_embedding = FaceEmbedding(
                worker_id=new_worker.worker_id,
                embedding_vector=embedding_vector
            )
            db.add(new_embedding)

        db.commit()
        db.refresh(new_worker)
        return new_worker
        
    except IntegrityError:
        # Catches DB-level unique constraint violations (e.g., race conditions)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error. Worker with this ID or Tag already exists."
        )
    except Exception as e:
        # Catches all other random crashes
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database transaction failed. Registration rolled back."
        )

async def identify_worker_service(db: Session, face_image: UploadFile) -> dict:
    image_bytes = await face_image.read()
    result = generate_embedding(image_bytes)

    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error")
        )

    target_embedding = result["embedding"]

    # Explicit dimension validation
    if len(target_embedding) != EXPECTED_EMBEDDING_DIMENSION:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Model returned invalid embedding dimension. Expected {EXPECTED_EMBEDDING_DIMENSION}."
        )

    closest_match = db.query(
        FaceEmbedding,
        FaceEmbedding.embedding_vector.l2_distance(target_embedding).label("distance")
    ).order_by(asc("distance")).first()

    if not closest_match:
        return {"worker_id": None, "score": 0.0, "matched": False}

    face_record, distance = closest_match

    # Expose the raw distance directly. Removed the arbitrary percentage formula.
    score = round(distance, 4)

    if distance <= DEV_RECOGNITION_THRESHOLD:
        return {
            "worker_id": face_record.worker_id,
            "score": score, # Now returning the raw L2 distance as the score
            "matched": True
        }
    
    return {
        "worker_id": None,
        "score": score,
        "matched": False
    }