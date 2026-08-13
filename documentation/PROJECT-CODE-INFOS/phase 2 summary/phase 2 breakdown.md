# Phase 2 — Technical Setup & Foundation

## Objective

The objective of Phase 2 was to transform the project conception into a functional technical foundation. The development environment, database infrastructure, backend framework, database schema, and communication between the backend and PostgreSQL were established and tested.

The project remains based on the defined architecture:

**FastAPI + SQLAlchemy + PostgreSQL/pgvector + AI services + React frontend**

No AI functionality was implemented yet during this phase. The purpose was to create a stable foundation for the following development phases.

## 1. Project Structure

The project repository was organized into modular components:

```text
AI-PPE-Construction/
│
├── backend/
│   └── app/
│       ├── api/
│       ├── core/
│       ├── db/
│       ├── models/
│       ├── schemas/
│       ├── services/
│       ├── __init__.py
│       └── main.py
│
├── frontend/
│
├── ai/
│   ├── ppe_detection/
│   │   ├── training/
│   │   ├── evaluation/
│   │   └── notebooks/
│   ├── face_recognition/
│   │   └── experiments/
│   └── report_generation/
│       └── experiments/
│
├── database/
│   ├── init/
│   └── migrations/
│
├── dataset/
│   ├── raw/
│   ├── annotated/
│   ├── train/
│   ├── val/
│   └── test/
│
├── models/
├── videos/
├── outputs/
│   └── reports/
├── tests/
├── documentation/
│
├── .gitignore
├── .env.example
├── docker-compose.yml
├── requirements.txt
└── README.md
```

The structure separates AI experimentation and training from backend application services and keeps datasets, videos, models, outputs, and documentation independent from application code.

## 2. Python Environment

A Python virtual environment was created for the project:

```bash
python -m venv .venv
```

The environment is activated before development.

The project dependencies are defined in `requirements.txt`, including:

* FastAPI
* Uvicorn
* Pydantic
* python-dotenv
* HTTPX
* python-multipart
* SQLAlchemy
* Psycopg
* pgvector
* Alembic
* PyTorch
* Torchvision
* Ultralytics
* InsightFace
* ONNX Runtime
* OpenCV
* NumPy

The `.venv` directory is excluded from Git.

## 3. Docker and PostgreSQL

Docker Compose was configured to run PostgreSQL with the pgvector extension.

The database service uses:

```text
PostgreSQL 16
+
pgvector
```

A persistent Docker volume is used so that the database data survives container restarts.

The database is configured through environment variables stored locally in `.env`.

Sensitive configuration is not committed to Git. `.env.example` provides the required variable names for the development team.

## 4. pgvector Initialization

The PostgreSQL `vector` extension is enabled through:

```text
database/init/01_extensions.sql
```

containing:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

The initialization directory is mounted into PostgreSQL's initialization directory through Docker Compose.

## 5. Database Schema

The conceptual class diagram was translated into seven PostgreSQL entities:

```text
administrators
workers
face_embeddings
attendance_records
video_sources
ppe_compliance_logs
daily_reports
```

### Relationships

```text
Worker 1 ───── 1..* FaceEmbedding

Worker 1 ───── 0..* AttendanceRecord

Worker 1 ───── 0..* PPEComplianceLog

VideoSource 1 ───── 0..* PPEComplianceLog
```

`DailyReport` is generated from aggregated attendance and PPE data and therefore does not contain direct foreign keys to individual attendance or PPE records.

## 6. SQLAlchemy Models

SQLAlchemy 2.0 models were implemented using the modern `Mapped` and `mapped_column` syntax.

The database models correspond to:

* `Administrator`
* `Worker`
* `FaceEmbedding`
* `AttendanceRecord`
* `VideoSource`
* `PPEComplianceLog`
* `DailyReport`

### Important project-specific design decisions

Worker identifiers use UUIDs.

`employee_id` is unique.

`tag_id` is optional and unique.

A worker can have multiple face embeddings.

A worker can have multiple attendance records over time.

A worker can have multiple PPE compliance logs.

A video can generate multiple PPE compliance logs.

Attendance records enforce one record per worker per date using a unique constraint on:

```text
(worker_id, date)
```

PPE timestamps represent the position in a pre-recorded video in seconds.

PPE compliance status is represented by a controlled enum:

```text
FULL_PPE
HELMET_MISSING
VEST_MISSING
NO_PPE
```

Daily attendance and PPE summaries are stored as PostgreSQL `JSONB`.

## 7. Face Embedding Storage

The `face_embeddings` table uses the PostgreSQL `vector` type through pgvector.

The current schema uses:

```text
VECTOR(512)
```

This corresponds to the current project design. The exact InsightFace model and resulting embedding dimension will be verified before permanently freezing future model-related database changes.

## 8. Alembic Migrations

Alembic was initialized for controlled database schema management.

The migration environment was configured in:

```text
database/migrations/env.py
```

The configuration performs two important tasks:

1. Loads the PostgreSQL `DATABASE_URL` from `.env`.
2. Imports the backend database models so Alembic can access `Base.metadata`.

The initial migration was generated:

```text
84c2666ad27e_initial_database_schema
```

The migration was successfully applied using:

```bash
alembic upgrade head
```

## 9. FastAPI Backend

A basic FastAPI application was created in:

```text
backend/app/main.py
```

The application currently exposes:

```text
GET /
GET /health
GET /health/database
```

The root endpoint confirms that the API is running.

The health endpoint confirms that FastAPI is operational.

The database health endpoint verifies the connection between FastAPI, SQLAlchemy, and PostgreSQL.

## 10. Database Session Management

The backend database layer contains:

```text
backend/app/db/base.py
backend/app/db/database.py
backend/app/db/dependencies.py
```

`base.py` defines the SQLAlchemy declarative base.

`database.py` creates the SQLAlchemy engine and session factory using the `DATABASE_URL`.

`dependencies.py` provides FastAPI with a database session for individual requests and ensures the session is closed correctly.

## 11. Verification Tests

The following infrastructure components were successfully tested:

```text
Python virtual environment       ✅
Dependencies installed           ✅
Docker PostgreSQL container      ✅
pgvector extension               ✅
Alembic migration                ✅
Seven project database tables    ✅
FastAPI application              ✅
FastAPI /health                  ✅
FastAPI /health/database         ✅
SQLAlchemy → PostgreSQL          ✅
Worker table query               ✅
```

A temporary `/test/workers` endpoint was used to verify that FastAPI could query the `workers` table through SQLAlchemy.

The endpoint returned:

```json
{
  "workers": []
}
```

because no workers had been registered yet.

The temporary `test.py` file and its router were then removed because they were only used for infrastructure validation.

## 12. Phase 2 Result

At the end of Phase 2, the project has a working technical foundation:

```text
FastAPI
   ↓
SQLAlchemy
   ↓
PostgreSQL
   +
pgvector
   +
Alembic
```

The database schema is created and version-controlled through migrations, and the backend is successfully communicating with the database.

The system is now ready for the first functional AI module:

**Phase 3 — Worker Enrollment & Face Recognition.**
