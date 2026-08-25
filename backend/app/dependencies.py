# [ADDED FILE] Dedicated dependencies module to prevent circular imports
from fastapi import Request
from app.services.face_recognition import FaceRecognitionService


def get_face_service(request: Request) -> FaceRecognitionService:
    # [ADDED] Inject face_service directly from app.state
    return request.app.state.face_service