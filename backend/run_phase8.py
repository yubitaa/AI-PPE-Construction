import json
from datetime import date

# Import the existing DB configuration instead of hardcoding
from app.db.database import SessionLocal
from app.services.analytics import generate_daily_analytics

def main():
    # Use the configured SessionLocal
    with SessionLocal() as db:
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