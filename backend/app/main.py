from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db.dependencies import get_db

# Import the newly created router
from app.api import workers

app = FastAPI(
    title="AI-Based Construction Worker Attendance & PPE Compliance System",
    version="0.1.0",
)

# Wire the router into the application
app.include_router(workers.router)

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
def database_health_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {
        "status": "ok",
        "database": "connected",
    }