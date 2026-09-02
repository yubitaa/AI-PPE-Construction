from datetime import date
from sqlalchemy.orm import Session
from app.models.ppe_log import PPEComplianceLog, PPEStatus
from app.models.attendance import AttendanceRecord
from app.models.daily_report import DailyReport

def generate_daily_analytics(db: Session, target_date: date) -> DailyReport:
    """
    Phase 8 Analytics Engine: Aggregates attendance and PPE logs for a given date.
    """
    # 1. Fetch Attendance Records for the target date
    attendances = db.query(AttendanceRecord).filter(AttendanceRecord.record_date == target_date).all()
    
    # 2. Build the structured attendance summary
    attendance_summary = {
        "total_present": len(attendances),
        "workers": [
            {
                "worker_id": str(a.worker_id),
                "name": a.worker.name,
                "clock_in": a.clock_in.isoformat(),
                "status": a.status
            } for a in attendances
        ]
    }

    # 3. Fetch all PPE Logs for the workers present today
    # (Since timestamp is video-relative, we filter by the workers who were clocked in today)
    present_worker_ids = [a.worker_id for a in attendances]
    
    if present_worker_ids:
        ppe_logs = db.query(PPEComplianceLog).filter(PPEComplianceLog.worker_id.in_(present_worker_ids)).all()
    else:
        ppe_logs = []

    # 4. Calculate Global PPE Statistics
    total_events = len(ppe_logs)
    full_ppe = sum(1 for log in ppe_logs if log.compliance_status == PPEStatus.FULL_PPE)
    helmet_missing = sum(1 for log in ppe_logs if log.compliance_status == PPEStatus.HELMET_MISSING)
    vest_missing = sum(1 for log in ppe_logs if log.compliance_status == PPEStatus.VEST_MISSING)
    no_ppe = sum(1 for log in ppe_logs if log.compliance_status == PPEStatus.NO_PPE)
    
    # Safe calculation to avoid zero-division (Section 19: Test 5)
    global_compliance_rate = (full_ppe / total_events * 100.0) if total_events > 0 else 0.0

    # 5. Calculate Worker-Level Statistics
    worker_stats = {}
    for log in ppe_logs:
        wid = str(log.worker_id)
        if wid not in worker_stats:
            worker_stats[wid] = {
                "worker_id": wid,
                "name": log.worker.name,
                "total_events": 0,
                "full_ppe": 0,
                "helmet_missing": 0,
                "vest_missing": 0,
                "no_ppe": 0
            }
        
        worker_stats[wid]["total_events"] += 1
        
        if log.compliance_status == PPEStatus.FULL_PPE:
            worker_stats[wid]["full_ppe"] += 1
        elif log.compliance_status == PPEStatus.HELMET_MISSING:
            worker_stats[wid]["helmet_missing"] += 1
        elif log.compliance_status == PPEStatus.VEST_MISSING:
            worker_stats[wid]["vest_missing"] += 1
        elif log.compliance_status == PPEStatus.NO_PPE:
            worker_stats[wid]["no_ppe"] += 1

    # Finalize worker compliance rates
    worker_breakdowns = []
    for wid, stats in worker_stats.items():
        w_total = stats["total_events"]
        w_full = stats["full_ppe"]
        stats["compliance_rate"] = round((w_full / w_total * 100.0), 2) if w_total > 0 else 0.0
        worker_breakdowns.append(stats)

    # 6. Build the structured PPE summary
    ppe_summary = {
        "total_events": total_events,
        "violations_breakdown": {
            "full_ppe": full_ppe,
            "helmet_missing": helmet_missing,
            "vest_missing": vest_missing,
            "no_ppe": no_ppe
        },
        "worker_statistics": worker_breakdowns
    }

    # 7. Create or Update the DailyReport in the database
    report = db.query(DailyReport).filter(DailyReport.report_date == target_date).first()
    if not report:
        report = DailyReport(
            report_date=target_date,
            attendance_summary=attendance_summary,
            ppe_summary=ppe_summary,
            compliance_rate=global_compliance_rate,
            report_content=""  # Phase 9 will fill this in!
        )
        db.add(report)
    else:
        report.attendance_summary = attendance_summary
        report.ppe_summary = ppe_summary
        report.compliance_rate = global_compliance_rate

    db.commit()
    db.refresh(report)
    
    return report