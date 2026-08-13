What each group covers

Backend/API

FastAPI → backend API
Uvicorn → runs FastAPI
Pydantic → API data validation
python-dotenv → .env configuration
httpx → communication with the local SLM/runtime
python-multipart → uploading worker images and video files

Database

SQLAlchemy → database ORM
Psycopg → PostgreSQL connection
pgvector → facial embedding storage/search

CV/AI

PyTorch + Torchvision → deep-learning foundation
Ultralytics → YOLO + tracking
InsightFace → face detection/recognition/embeddings
ONNX Runtime → InsightFace inference
OpenCV → image/video processing
NumPy → numerical/image/embedding operations
One thing we're deliberately NOT adding yet

We are not adding an SLM-specific package because we haven't chosen the SLM runtime yet.

Likewise, we're not adding OCR, Redis, LangChain, cloud SDKs, etc., because those are not part of our current core implementation.

So yes:

This is our current requirements.txt.