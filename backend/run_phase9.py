from datetime import date
from app.db.database import SessionLocal
from app.services.report_generator import generate_daily_safety_report

def main():
    print("🤖 Booting up Phase 9 SLM Generator...\n")
    with SessionLocal() as db:
        today = date.today()
        
        try:
            # Call the Phase 9 service
            report = generate_daily_safety_report(db, target_date=today)
            
            print("✅ REPORT SUCCESSFULLY GENERATED!\n")
            print("==================================================")
            print(report.report_content)
            print("==================================================")
            print("\nData successfully saved to 'daily_reports.report_content'.")
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    main()