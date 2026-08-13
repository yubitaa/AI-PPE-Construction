Step 4 — Database Schema Design & Creation

We will do this in 6 small parts.

4.1 Finalize the database entities

From our class diagram, we have these 7 tables:

administrators
workers
face_embeddings
attendance_records
video_sources
ppe_compliance_logs
daily_reports

We already defined the relationships, so now we translate them into actual database columns and foreign keys.

4.2 Define each table's columns and data types

For example, workers will contain things like:

worker_id
name
employee_id
role
department
tag_id

Then we decide:

UUID or integer IDs
text vs timestamp vs boolean
nullable fields
unique fields
default values

We do this for all 7 tables.

4.3 Define the relationships / foreign keys

We'll implement the relationships we finalized:

workers
   │
   ├── face_embeddings
   ├── attendance_records
   └── ppe_compliance_logs
                    ▲
                    │
              video_sources

For example:

face_embeddings.worker_id
        → workers.worker_id

attendance_records.worker_id
        → workers.worker_id

ppe_compliance_logs.worker_id
        → workers.worker_id

ppe_compliance_logs.video_id
        → video_sources.video_id

No artificial foreign keys for daily_reports.

4.4 Handle facial embeddings with pgvector

This is an important part.

face_embeddings.embedding_vector will use PostgreSQL's vector type so we can later perform similarity searches.

But we should not blindly hard-code vector(512) yet.

First we confirm the exact InsightFace model we are going to use and the dimension it actually produces.

Then the schema will use the correct dimension.

4.5 Add constraints and indexes

We'll decide things like:

employee_id → UNIQUE
username → UNIQUE
attendance → unique per worker/date

And indexes for fields we search frequently, especially:

worker_id
date
timestamp
video_id

For face embeddings, we'll later decide the appropriate pgvector index once we know the embedding setup.

4.6 Create the database schema

Once the design is approved, we'll actually create it.

For our project, I recommend:

SQLAlchemy models
        ↓
Alembic migrations
        ↓
PostgreSQL

This gives us a controlled way to modify the schema later without manually deleting/recreating the database.

That means we would add Alembic to the backend dependencies in this step.

What Step 4 should produce

By the end of this step, we should have:

✅ Final database ER/schema
✅ 7 database tables
✅ Primary keys
✅ Foreign keys
✅ Constraints
✅ Indexes
✅ pgvector configured
✅ Initial migration
✅ Database running in Docker
✅ Schema successfully created in PostgreSQL

And then we can verify the database actually contains:

administrators
workers
face_embeddings
attendance_records
video_sources
ppe_compliance_logs
daily_reports
One important rule



in details
Step 4.1 — Finalize the 7 database tables

These are the tables we already agreed on:

administrators
workers
face_embeddings
attendance_records
video_sources
ppe_compliance_logs
daily_reports

Before writing SQLAlchemy models, we need to define exactly what each table contains.

1. administrators

For admin authentication.

admin_id
username
password_hash

username should be unique.

2. workers

This is the central table.

worker_id
name
employee_id
role
department
tag_id

Constraints:

employee_id → UNIQUE
tag_id       → UNIQUE, nullable

tag_id is optional because our tag/QR mechanism is optional.

3. face_embeddings

A worker can have multiple reference embeddings.

embedding_id
worker_id
embedding_vector
created_at

Relationship:

workers 1 ───── 1..* face_embeddings

worker_id is a foreign key to workers.

Important

We should not decide the vector dimension yet.

Before defining something like:

vector(512)

we should verify exactly which InsightFace model we use and what embedding dimension it produces.

4. attendance_records

For daily clock-in.

attendance_id
worker_id
date
clock_in
status

Relationship:

workers 1 ───── 0..* attendance_records

Important constraint:

(worker_id, date) → UNIQUE

This guarantees one attendance record per worker per day and supports our "already clocked in" logic.

5. video_sources

Represents the pre-recorded videos we use for monitoring.

video_id
file_name
file_path
uploaded_at
duration
status

Relationship:

video_sources 1 ───── 0..* ppe_compliance_logs
6. ppe_compliance_logs

This stores PPE observations/events.

log_id
worker_id
video_id
timestamp
helmet_detected
vest_detected
compliance_status

Relationships:

workers      1 ───── 0..* ppe_compliance_logs

video_sources 1 ───── 0..* ppe_compliance_logs

The compliance status can be:

FULL_PPE
HELMET_MISSING
VEST_MISSING
NO_PPE

We should store this as a controlled value rather than arbitrary text.

7. daily_reports

Represents the generated daily report.

report_id
report_date
generated_at
attendance_summary
ppe_summary
compliance_rate
report_content

There is no foreign key to attendance or PPE logs.

The report is generated from aggregated data.

Step 4.2 — Final relationship map
                    administrators
                         │
                         │ authentication
                         │
                    ┌────┴────┐
                    │         │
                    ▼         ▼
                 workers   daily_reports
                    │
          ┌─────────┼──────────┐
          │         │          │
          ▼         ▼          ▼
 face_embeddings  attendance  PPE logs
                               ▲
                               │
                               │
                         video_sources

More explicitly:

Worker
 ├── 1..* FaceEmbedding
 ├── 0..* AttendanceRecord
 └── 0..* PPEComplianceLog

VideoSource
 └── 0..* PPEComplianceLog
Step 4.3 — One thing we should decide before implementation

There are three technical choices I don't want us to guess:

IDs

I recommend using UUIDs for the main IDs rather than auto-increment integers.

That gives us:

worker_id UUID
attendance_id UUID
...

It is cleaner for an API-based application and avoids exposing sequential IDs.

Dates/timestamps

Use PostgreSQL timestamp types for events and timezone-aware timestamps where appropriate.

PPE status

Use a controlled enum rather than unrestricted strings.

So our immediate task

Before we create any files or models, we should lock these choices:

1. UUID vs integer IDs
2. Exact timestamp types
3. PPE status enum
4. Exact FaceEmbedding vector dimension

I recommend:

UUID + timezone-aware timestamps + PPE enum + vector dimension based on the exact InsightFace model we select. 
this was done before we write the ctual python code for our database
