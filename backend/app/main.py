from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI  # [MODIFIED] Removed unused Request import
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api import workers
from app.db.dependencies import get_db
from app.services.face_recognition import FaceRecognitionService


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.face_service = FaceRecognitionService()
    yield
    app.state.face_service = None


app = FastAPI(
    title="AI-Based Construction Worker Attendance & PPE Compliance System",
    version="0.1.0",
    lifespan=lifespan,
)

# [REMOVED] get_face_service definition moved to app/dependencies.py

app.include_router(workers.router)


@app.get("/")
def root():
    return {"message": "PPE Monitoring API is running."}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/health/database")
def database_health_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {
        "status": "ok",
        "database": "connected",
    }