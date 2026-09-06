import uuid
from datetime import date, datetime, timezone

# Import the existing DB configuration instead of hardcoding
from app.db.database import SessionLocal

# Import your database models
from app.models.ppe_log import PPEComplianceLog, PPEStatus
from app.models.attendance import AttendanceRecord
from app.models.worker import Worker
from app.models.video_source import VideoSource

def seed_mock_data():
    # Use the configured SessionLocal
    with SessionLocal() as db:
        print("Cleaning up previous mock data safely...")
        
        # 1. Safely delete ONLY the mock records (protects real database data)
        mock_employee_ids = ["MOCK-EMP-A1", "MOCK-EMP-B2", "MOCK-EMP-C3"]
        mock_workers = db.query(Worker).filter(Worker.employee_id.in_(mock_employee_ids)).all()
        mock_worker_ids = [w.worker_id for w in mock_workers]
        
        if mock_worker_ids:
            db.query(PPEComplianceLog).filter(PPEComplianceLog.worker_id.in_(mock_worker_ids)).delete(synchronize_session=False)
            db.query(AttendanceRecord).filter(AttendanceRecord.worker_id.in_(mock_worker_ids)).delete(synchronize_session=False)
            db.commit()

        # 2. Ensure we have mock Workers and a Video
        worker_a = db.query(Worker).filter_by(employee_id="MOCK-EMP-A1").first()
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
            worker_b = db.query(Worker).filter_by(employee_id="MOCK-EMP-B2").first()
            worker_c = db.query(Worker).filter_by(employee_id="MOCK-EMP-C3").first()
            # FIXED: Explicitly select the mock video instead of just .first()
            video = db.query(VideoSource).filter_by(file_name="test_cam_1.mp4").first()

        today = date.today()
        now = datetime.now(timezone.utc)
        # ADD THESE TWO LINES: Force the mock video to belong to "today"
        video.uploaded_at = now
        db.commit()
        # 3. Create Attendance Records for Today
        print("Seeding Attendance Records...")
        db.add_all([
            AttendanceRecord(worker_id=worker_a.worker_id, record_date=today, clock_in=now, status="PRESENT"),
            AttendanceRecord(worker_id=worker_b.worker_id, record_date=today, clock_in=now, status="PRESENT"),
            AttendanceRecord(worker_id=worker_c.worker_id, record_date=today, clock_in=now, status="PRESENT"),
        ])

        # 4. Create PPE Logs matching Phase 8 Spec (Section 19)
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