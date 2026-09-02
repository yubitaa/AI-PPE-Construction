import uuid
from datetime import date, datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Import your database models
from app.models.ppe_log import PPEComplianceLog, PPEStatus
from app.models.attendance import AttendanceRecord
from app.models.worker import Worker
from app.models.video_source import VideoSource

# Connect directly to your Docker database
DATABASE_URL = "postgresql://admin:change_me@localhost:5432/ppe_monitoring"
engine = create_engine(DATABASE_URL)

def seed_mock_data():
    with Session(engine) as db:
        print("Clearing old mock data...")
        db.query(PPEComplianceLog).delete()
        db.query(AttendanceRecord).delete()
        
        # 1. Ensure we have mock Workers and a Video (FIXED: Unique MOCK employee IDs)
        worker_a = db.query(Worker).filter_by(name="Worker A").first()
        if not worker_a:
            worker_a = Worker(worker_id=uuid.uuid4(), name="Worker A", employee_id="MOCK-EMP-A1", role="Builder", department="Construction")
            worker_b = Worker(worker_id=uuid.uuid4(), name="Worker B", employee_id="MOCK-EMP-B2", role="Welder", department="Metalwork")
            worker_c = Worker(worker_id=uuid.uuid4(), name="Worker C", employee_id="MOCK-EMP-C3", role="Foreman", department="Management")
            db.add_all([worker_a, worker_b, worker_c])
            
            video = VideoSource(
                video_id=uuid.uuid4(), 
                file_name="test_cam_1.mp4",
                file_path="/videos/test_cam_1.mp4",
                status="PROCESSED"
            )
            db.add(video)
            db.commit()
        else:
            worker_b = db.query(Worker).filter_by(name="Worker B").first()
            worker_c = db.query(Worker).filter_by(name="Worker C").first()
            video = db.query(VideoSource).first()

        today = date.today()
        now = datetime.now(timezone.utc)

        # 2. Create Attendance Records for Today
        print("Seeding Attendance Records...")
        db.add_all([
            AttendanceRecord(worker_id=worker_a.worker_id, record_date=today, clock_in=now, status="PRESENT"),
            AttendanceRecord(worker_id=worker_b.worker_id, record_date=today, clock_in=now, status="PRESENT"),
            AttendanceRecord(worker_id=worker_c.worker_id, record_date=today, clock_in=now, status="PRESENT"),
        ])

        # 3. Create PPE Logs matching Phase 8 Spec (Section 19)
        print("Seeding PPE Compliance Logs...")
        
        logs = []
        
        # Test 1: Worker A - Full PPE only (100% compliance)
        for t in [10.0, 11.5, 13.0]:
            logs.append(PPEComplianceLog(
                worker_id=worker_a.worker_id, video_id=video.video_id, timestamp=t, 
                helmet_detected=True, vest_detected=True, compliance_status=PPEStatus.FULL_PPE
            ))

        # Test 2: Worker B - Mixed PPE states (40% compliance)
        mixed_states = [
            PPEStatus.FULL_PPE, PPEStatus.FULL_PPE, 
            PPEStatus.HELMET_MISSING, PPEStatus.VEST_MISSING, PPEStatus.NO_PPE
        ]
        for i, state in enumerate(mixed_states):
            logs.append(PPEComplianceLog(
                worker_id=worker_b.worker_id, video_id=video.video_id, timestamp=float(i+20), 
                helmet_detected=(state in [PPEStatus.FULL_PPE, PPEStatus.VEST_MISSING]), 
                vest_detected=(state in [PPEStatus.FULL_PPE, PPEStatus.HELMET_MISSING]), 
                compliance_status=state
            ))

        # Test 3: Worker C - Worker-level aggregation (66.67% compliance)
        logs.append(PPEComplianceLog(worker_id=worker_c.worker_id, video_id=video.video_id, timestamp=30.1, helmet_detected=True, vest_detected=True, compliance_status=PPEStatus.FULL_PPE))
        logs.append(PPEComplianceLog(worker_id=worker_c.worker_id, video_id=video.video_id, timestamp=31.2, helmet_detected=True, vest_detected=True, compliance_status=PPEStatus.FULL_PPE))
        logs.append(PPEComplianceLog(worker_id=worker_c.worker_id, video_id=video.video_id, timestamp=32.3, helmet_detected=False, vest_detected=True, compliance_status=PPEStatus.HELMET_MISSING))

        db.add_all(logs)
        db.commit()
        print("✅ Mock Data successfully seeded!")

if __name__ == "__main__":
    seed_mock_data()