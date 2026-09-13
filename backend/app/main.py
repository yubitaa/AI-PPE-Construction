from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api import attendance, ppe, reports, workers
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


# Registering routers under the official /api/v1 contract
app.include_router(workers.router, prefix="/api/v1/workers", tags=["Workers"])
app.include_router(attendance.router, prefix="/api/v1/attendance", tags=["Attendance"])
app.include_router(ppe.router, prefix="/api/v1/ppe", tags=["PPE Compliance"])
app.include_router(reports.router, prefix="/api/v1", tags=["Analytics & Reports"])


@app.get("/")
def root():
    return {
        "message": "PPE Monitoring API is running."
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }


@app.get("/health/database")
def database_health_check(
    db: Session = Depends(get_db),
):
    db.execute(text("SELECT 1"))

    return {
        "status": "ok",
        "database": "connected",
    }