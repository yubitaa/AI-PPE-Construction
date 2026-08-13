AI-PPE-Construction/
│
├── backend/
│   └── app/
│       ├── api/
│       │   └── __init__.py
│       │
│       ├── core/
│       │   └── __init__.py
│       │
│       ├── db/
│       │   └── __init__.py
│       │
│       ├── models/
│       │   └── __init__.py
│       │
│       ├── schemas/
│       │   └── __init__.py
│       │
│       ├── services/
│       │   └── __init__.py
│       │
│       ├── __init__.py
│       └── main.py
│
├── frontend/
│   └── README.md
│
├── ai/
│   ├── ppe_detection/
│   │   ├── training/
│   │   ├── evaluation/
│   │   └── notebooks/
│   │
│   ├── face_recognition/
│   │   └── experiments/
│   │
│   └── report_generation/
│       └── experiments/
│
├── database/
│   ├── init/
│   ├── schema/
│   └── seeds/
│
├── dataset/
│   ├── raw/
│   ├── annotated/
│   ├── train/
│   ├── val/
│   └── test/
│
├── models/
│   └── README.md
│
├── videos/
│   └── README.md
│
├── outputs/
│   └── reports/
│
├── tests/
│
├── documentation/
│
├── .gitignore
├── .env.example
├── docker-compose.yml
├── requirements.txt
└── README.md

2. What every part is for
backend/

This is your FastAPI application.

It contains the code that actually runs the system.

backend/
└── app/

We deliberately put the application inside app/ so the backend stays organized and imports remain clean.

backend/app/api/

Contains your API routes/endpoints.

For example, later you may have:

POST /workers
GET  /workers
POST /attendance/clock-in
GET  /attendance
POST /videos/process
GET  /ppe-events
GET  /reports

So this folder answers:

How does the frontend communicate with the backend?

backend/app/core/

Contains core application configuration.

Later this can contain things like:

config.py
security.py

For example:

reading environment variables
authentication configuration
application settings

Keep it empty for now except __init__.py.

backend/app/db/

Everything related to the database connection.

Later:

database.py
session.py

This is where FastAPI gets its PostgreSQL connection.

backend/app/models/

These are the database/domain models.

This folder corresponds closely to the classes we just designed.

Later you will have models such as:

worker.py
face_embedding.py
attendance.py
ppe_log.py
video_source.py
daily_report.py
administrator.py

Important:

This models/ is not the same thing as the root models/ folder.

Here:

backend/app/models/

means database/application models.

While:

models/

at the root means AI model files such as YOLO weights.

backend/app/schemas/

Contains the data structures used when data enters or leaves the API.

For example:

WorkerCreate
WorkerResponse
AttendanceResponse
PPELogResponse
ReportResponse

This keeps your API data separate from your database models.

backend/app/services/

This is very important.

This is where the backend calls the actual AI functionality.

Later you might have:

face_service.py
ppe_service.py
video_service.py
report_service.py
analytics_service.py

For example:

API
 ↓
ppe_service.py
 ↓
YOLO model
 ↓
result
 ↓
database

This is the solution to the ai/ vs backend/ import problem we discussed.

3. backend/app/main.py

This is the FastAPI entry point.

Later:

main.py

will create the FastAPI application and register your API routes.

Conceptually:

main.py
   ↓
FastAPI
   ↓
API routes
   ↓
Services
   ↓
Database / AI
4. frontend/

This is your React application.

We are deliberately not building the React structure yet.

Once we initialize the React project, it will create its own structure such as:

frontend/
├── src/
├── public/
├── package.json
└── ...

So for now, just keep the folder.

The frontend will eventually handle:

Admin login
Worker management
Attendance view
Safety dashboard
Video monitoring
Reports
5. ai/

This is AI development and experimentation.

This folder is different from backend/app/services/.

ai/ppe_detection/

Your main AI engineering work.

ppe_detection/
├── training/
├── evaluation/
└── notebooks/
training/

For:

dataset preparation
training scripts
fine-tuning YOLO
augmentation experiments
evaluation/

For:

Precision
Recall
mAP
confusion matrices
error analysis
notebooks/

For exploratory experiments and visual analysis.

ai/face_recognition/

Contains experiments related to InsightFace.

For example:

testing recognition thresholds
testing different reference images
comparing embeddings
recognition experiments

We are not training a face-recognition model from scratch.

ai/report_generation/

Contains experiments for the SLM, not an LLM.

Later this can contain:

prompt experiments
model comparison
report quality evaluation
local SLM tests

The actual application integration will eventually live in:

backend/app/services/report_service.py
6. database/

This folder contains database-related files.

database/init/

Initialization scripts used when setting up the database.

database/schema/

Your database schema/migrations/scripts.

Eventually this will correspond to:

workers
face_embeddings
attendance_records
ppe_compliance_logs
video_sources
daily_reports
administrators
database/seeds/

Optional sample/test data.

For example:

3 demo workers
sample attendance
sample PPE records

Useful when testing the dashboard.

7. dataset/

This is your PPE dataset.

dataset/
├── raw/
├── annotated/
├── train/
├── val/
└── test/
raw/

Original images/videos.

annotated/

Labeled images before organizing them into training splits.

train/

Training data.

val/

Validation data.

test/

Final holdout test data.

This separation is important because your evaluation needs data that the model did not train on.

8. Root models/

This is where trained AI model files go.

For example:

models/
├── README.md
├── ppe_best.pt
└── ...

However, because model weights can be very large, we will not commit them to GitHub unless there is a specific reason.

The README.md will explain:

what model files are needed
where they come from
how to obtain them
which version is used
9. videos/

This is specifically for your project because we've established:

No live camera/RTSP implementation.

These are your test inputs:

videos/
├── site_test_01.mp4
├── site_test_02.mp4
└── ...

These should normally be ignored by Git because they can become very large.

10. outputs/reports/

This is where the system-generated reports go.

For example:

outputs/
└── reports/
    ├── safety_report_2026-08-20.pdf
    ├── safety_report_2026-08-21.pdf
    └── ...

These are generated by the application.

11. tests/

All tests eventually go here.

For example:

tests/
├── test_workers.py
├── test_attendance.py
├── test_ppe.py
└── test_reports.py

Don't create those yet.

12. documentation/

Everything related to your project documentation.

For example:

documentation/
├── Project_Conception.docx
├── diagrams/
├── report/
└── presentation/

You can move your existing Word conception here.

13. .gitignore

Very important.

It prevents Git from uploading things that should stay local.

It should eventually ignore things such as:

.env
.venv/
__pycache__/
*.pyc

dataset/raw/
dataset/annotated/
dataset/train/
dataset/val/
dataset/test/

videos/*
outputs/reports/*
models/*.pt
models/*.onnx

We will write the exact .gitignore in the next step rather than guessing it now.

14. .env.example

This is a template showing what environment variables the project needs.

Something like:

DATABASE_URL=
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=

SLM_MODEL=
SLM_BASE_URL=

The real values will go in:

.env

and .env will not be committed to Git.

15. docker-compose.yml

This is where Docker comes in.

For now, Docker should handle only PostgreSQL + pgvector.

Conceptually:

docker-compose.yml
        │
        ▼
PostgreSQL Container
        │
        └── pgvector

You do not need to put FastAPI, React, YOLO, or the SLM in Docker at this stage.

This keeps Docker useful without turning the project into a DevOps project.

16. requirements.txt

This lists the Python dependencies required by your project.

Eventually it will contain things like:

fastapi
uvicorn
sqlalchemy
psycopg
pgvector
opencv-python
insightface
torch
...

We will choose exact versions during Step 2.

Don't install random libraries one by one yet.

17. README.md

This is your project's entry point for the team.

It should eventually explain:

Project
Purpose
Architecture
Installation
How to run
Database setup
How to run AI models
How to run backend
How to run frontend

For now, it can simply contain the project title and a short description.


The final architecture of the codebase

The important relationship is:
                    AI DEVELOPMENT
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
            PPE       Face        SLM
         Training     Experiments  Experiments
              │          │          │
              └──────────┼──────────┘
                         │
                    Final Models
                         │
                         ▼
                  BACKEND SERVICES
                         │
             ┌───────────┼────────────┐
             ▼           ▼            ▼
          FastAPI      AI Services   Analytics
             │           │            │
             └───────────┼────────────┘
                         ▼
                  PostgreSQL
                    + pgvector
                         │
                         ▼
                     FRONTEND
                         │
                         ▼
                      ADMIN

And our actual data sources are:

Worker Photos ───────► Face Recognition

PPE Dataset ─────────► YOLO Training

Test Videos ─────────► YOLO + ByteTrack + Identification                      