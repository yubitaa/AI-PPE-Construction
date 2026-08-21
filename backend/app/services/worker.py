from typing import Optional

import cv2
import numpy as np
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import asc
from sqlalchemy.orm import Session

from app.models.face_embedding import FaceEmbedding
from app.models.worker import Worker
from app.services.face_recognition import FaceRecognitionService


EXPECTED_EMBEDDING_DIMENSION = 512
# Temporary development threshold: requires at least 60% resemblance to match
DEV_MIN_ACCURACY_THRESHOLD = 75.0

face_recognition_service = FaceRecognitionService()


async def register_worker_service(
    db: Session,
    name: str,
    employee_id: str,
    role: str,
    department: str,
    tag_id: Optional[str],
    face_images: list[UploadFile],
) -> Worker:
    # 1. Validate image count boundary (3-5 images)
    if not (3 <= len(face_images) <= 5):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration requires between 3 and 5 face images.",
        )

    # 2. Application-level duplicate checks
    if db.query(Worker).filter(Worker.employee_id == employee_id).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Worker with employee ID '{employee_id}' already exists.",
        )

    if tag_id and db.query(Worker).filter(Worker.tag_id == tag_id).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Worker with tag ID '{tag_id}' already exists.",
        )

    # 3. Process ALL images first.
    #    Nothing is written to PostgreSQL until every image succeeds.
    embeddings: list[list[float]] = []

    for index, image in enumerate(face_images):
        image_bytes = await image.read()

        # Decode uploaded image bytes into an OpenCV BGR image.
        image_array = np.frombuffer(image_bytes, dtype=np.uint8)
        decoded_image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        if decoded_image is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid image data on image {index + 1}.",
            )

        result = face_recognition_service.generate_embedding(decoded_image)

        result_status = result.get("status")

        if result_status != "SUCCESS":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Face recognition failed on image {index + 1}: "
                    f"{result_status}"
                ),
            )

        vector = result.get("embedding")

        if vector is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    f"Face recognition returned no embedding "
                    f"for image {index + 1}."
                ),
            )

        # 4. Verify the embedding dimension.
        if len(vector) != EXPECTED_EMBEDDING_DIMENSION:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    "Model returned invalid embedding dimension. "
                    f"Expected {EXPECTED_EMBEDDING_DIMENSION}, "
                    f"got {len(vector)}."
                ),
            )

        embeddings.append(vector)

    # 5. Only after ALL images succeeded, modify the database.
    try:
        new_worker = Worker(
            name=name,
            employee_id=employee_id,
            role=role,
            department=department,
            tag_id=tag_id,
        )

        db.add(new_worker)
        db.flush()

        # 6. Store all embeddings in the same transaction.
        for embedding_vector in embeddings:
            new_embedding = FaceEmbedding(
                worker_id=new_worker.worker_id,
                embedding_vector=embedding_vector,
            )
            db.add(new_embedding)

        # 7. Commit worker + every embedding together.
        db.commit()
        db.refresh(new_worker)

        return new_worker

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database transaction failed. Registration rolled back.",
        )


async def identify_worker_service(
    db: Session,
    face_image: UploadFile,
) -> dict:
    # Read uploaded image.
    image_bytes = await face_image.read()

    # Decode bytes into OpenCV BGR image.
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    decoded_image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    if decoded_image is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image data.",
        )

    # Generate the real face embedding.
    result = face_recognition_service.generate_embedding(decoded_image)

    result_status = result.get("status")

    if result_status != "SUCCESS":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result_status,
        )

    target_embedding = result.get("embedding")

    if target_embedding is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Face recognition returned no embedding.",
        )

    # Verify the embedding dimension.
    if len(target_embedding) != EXPECTED_EMBEDDING_DIMENSION:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Model returned invalid embedding dimension. "
                f"Expected {EXPECTED_EMBEDDING_DIMENSION}, "
                f"got {len(target_embedding)}."
            ),
        )

# PostgreSQL + pgvector nearest-neighbor search using Cosine distance.
    closest_match = (
        db.query(
            FaceEmbedding,
            FaceEmbedding.embedding_vector
            .cosine_distance(target_embedding) # Changed to cosine
            .label("distance"),
        )
        .order_by(asc("distance"))
        .first()
    )

    if not closest_match:
        return {
            "worker_id": None,
            "score": 0.0,
            "matched": False,
        }

    face_record, distance = closest_match

    # Convert Cosine Distance (0.0 to 2.0) into a 0-100% resemblance score
    # distance 0.0 becomes 100% match. distance 2.0 becomes 0% match.
    similarity_ratio = 1.0 - (distance / 2.0)
    accuracy_percentage = round(similarity_ratio * 100, 2)

    if accuracy_percentage >= DEV_MIN_ACCURACY_THRESHOLD:
        return {
            "worker_id": face_record.worker_id,
            "score": accuracy_percentage, # Safely keeping the 'score' key for the API contract
            "matched": True,
        }

    return {
        "worker_id": None,
        "score": accuracy_percentage,
        "matched": False,
    }