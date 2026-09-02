import json
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Connect directly to your Docker database
DATABASE_URL = "postgresql://admin:change_me@localhost:5432/ppe_monitoring"
engine = create_engine(DATABASE_URL)

from app.services.analytics import generate_daily_analytics

def main():
    with Session(engine) as db:
        today = date.today()
        print(f"Running Phase 8 Analytics for Date: {today}\n")
        
        # Call the service we just wrote
        report = generate_daily_analytics(db, target_date=today)
        
        print("📊 AGGREGATED COMPLIANCE RATE:")
        print(f"{report.compliance_rate:.2f}%\n")
        
        print("👷 ATTENDANCE SUMMARY (JSONB):")
        print(json.dumps(report.attendance_summary, indent=2))
        
        print("\n🦺 PPE SUMMARY & VIOLATIONS (JSONB):")
        print(json.dumps(report.ppe_summary, indent=2))
        
        print("\n✅ Phase 8 Aggregation Complete! Data saved to 'daily_reports' table.")

if __name__ == "__main__":
    main()