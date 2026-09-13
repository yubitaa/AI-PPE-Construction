from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.models.daily_report import DailyReport
from app.schemas.responses import DailyReportResponse  # Added strict response contract

from app.services.analytics import generate_daily_analytics
from app.services.report_generator import generate_daily_safety_report 

router = APIRouter(tags=["Analytics & Reports"])

class ReportGenerateRequest(BaseModel):
    target_date: date


# ---------------------------------------------------------
# ANALYTICS ENDPOINT (Phase 8 Integration)
# ---------------------------------------------------------

@router.get(
    "/analytics/{target_date}",
    response_model=DailyReportResponse,  # Added contract
    status_code=status.HTTP_200_OK
)
def get_daily_analytics(
    target_date: date,
    db: Session = Depends(get_db)
):
    """
    GET /api/v1/analytics/{date}
    Executes Phase 8 analytics engine and returns the structured DailyReport data.
    """
    try:
        report = generate_daily_analytics(db=db, target_date=target_date)
        return report
    except HTTPException:
        # FIXED: Pass through deliberate HTTPExceptions without converting to 500
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate analytics: {exc}"
        )


# ---------------------------------------------------------
# SLM REPORT ENDPOINTS (Phase 9 Integration)
# ---------------------------------------------------------

@router.post(
    "/reports/generate",
    response_model=DailyReportResponse,  # Added contract
    status_code=status.HTTP_200_OK
)
def generate_slm_report(
    request: ReportGenerateRequest,
    db: Session = Depends(get_db)
):
    """
    POST /api/v1/reports/generate
    Triggers Phase 9 Gemini SLM to analyze the data and generate the report_content.
    Payload: { "target_date": "YYYY-MM-DD" }
    """
    try:
        report = generate_daily_safety_report(db=db, target_date=request.target_date)
        
        if not report:
             raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No analytics data available to generate report for {request.target_date}."
            )
        return report
        
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to connect to SLM generation service: {exc}"
        )


@router.get(
    "/reports/{target_date}",
    response_model=DailyReportResponse,  # Added contract
    status_code=status.HTTP_200_OK
)
def get_existing_report(
    target_date: date,
    db: Session = Depends(get_db)
):
    """
    GET /api/v1/reports/{date}
    Fetches an already-generated daily report directly from the database.
    """
    report = db.query(DailyReport).filter(DailyReport.report_date == target_date).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report for {target_date} has not been generated yet."
        )
        
    return report