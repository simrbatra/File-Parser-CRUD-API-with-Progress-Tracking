# File-Parser-CRUD-API-with-Progress-Tracking
This backend application allows users to:

Upload files with progress tracking.

Parse uploaded files asynchronously (CSV/Excel/PDF).

Retrieve parsed content once ready.

Manage files with CRUD APIs.

Built with FastAPI, PostgreSQL (or SQLite), SQLAlchemy, Celery, and Redis.

# Setup Instructions
1. Clone Repository
git clone https:[//github.com/your-username/file-parser-api.git](https://github.com/simrbatra/File-Parser-CRUD-API-with-Progress-Tracking.git)
cd file-parser-api

2. Create Virtual Environment & Install Dependencies
python3 -m venv venv
source venv/bin/activate   # on Linux/Mac
venv\Scripts\activate      # on Windows

pip install -r requirements.txt

3. Configure Environment

Create a .env file:

DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/filedb
REDIS_URL=redis://localhost:6379/0

4. Run Database Migrations
alembic upgrade head

5. Start Services

Run FastAPI:

uvicorn app.main:app --reload


Run Celery worker:

celery -A app.worker.celery_app worker --loglevel=info

# API Documentation

Base URL: http://localhost:8000

1. Upload File

POST /files

Request: multipart/form-data

file: File to upload

Response

{
  "file_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "data.csv",
  "status": "uploading",
  "progress": 0
}

2. Check Upload Progress

GET /files/{file_id}/progress

Response (in progress):

{
  "file_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 65
}


Response (complete):

{
  "file_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "ready",
  "progress": 100
}

3. Get Parsed File Content

GET /files/{file_id}

Response (processing):

{
  "message": "File upload or processing in progress. Please try again later."
}


Response (ready):

{
  "file_id": "550e8400-e29b-41d4-a716-446655440000",
  "content": [
    { "name": "Alice", "age": 25 },
    { "name": "Bob", "age": 30 }
  ]
}

4. List Files

GET /files

Response

[
  {
    "file_id": "550e8400-e29b-41d4-a716-446655440000",
    "filename": "data.csv",
    "status": "ready",
    "created_at": "2025-08-20T12:34:56"
  },
  {
    "file_id": "440e8400-e29b-41d4-a716-446655440111",
    "filename": "report.pdf",
    "status": "processing",
    "created_at": "2025-08-20T12:40:22"
  }
]

5. Delete File

DELETE /files/{file_id}

Response

{
  "message": "File deleted successfully."
}

 Sample Testing (cURL)
Upload a File
curl -X POST "http://localhost:8000/files" \
  -F "file=@data.csv"

Check Progress
curl "http://localhost:8000/files/550e8400-e29b-41d4-a716-446655440000/progress"

Get Parsed Content
curl "http://localhost:8000/files/550e8400-e29b-41d4-a716-446655440000"

Delete File
curl -X DELETE "http://localhost:8000/files/550e8400-e29b-41d4-a716-446655440000"
