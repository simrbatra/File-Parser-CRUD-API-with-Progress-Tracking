from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from uuid import uuid4
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
from celery_worker import parse_file_task
import os
from datetime import datetime

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/files", status_code=201)
async def upload_file(file: UploadFile = File(...), db: Session = next(get_db())):
    file_id = str(uuid4())
    filepath = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")

    # Save file to disk streaming chunks
    with open(filepath, "wb") as buffer:
        while chunk := await file.read(1024*1024):
            buffer.write(chunk)

    # Save metadata
    new_file = models.File(
        id=file_id,
        filename=file.filename,
        status="uploading",
        progress=0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        filepath=filepath,
    )
    db.add(new_file)
    db.commit()

    # Trigger async parsing task via Celery
    parse_file_task.delay(file_id)

    return {"file_id": file_id, "status": "uploading", "progress": 0}

@app.get("/files/{file_id}/progress")
def get_progress(file_id: str, db: Session = next(get_db())):
    file = db.query(models.File).filter(models.File.id == file_id).first()
    if not file:
        raise HTTPException(404, "File not found")
    return {"file_id": file.id, "status": file.status, "progress": file.progress}

@app.get("/files/{file_id}")
def get_file_content(file_id: str, db: Session = next(get_db())):
    file = db.query(models.File).filter(models.File.id == file_id).first()
    if not file:
        raise HTTPException(404, "File not found")

    if file.status != "ready":
        return JSONResponse(status_code=202, content={"message": "File upload or processing in progress. Please try again later."})

    parsed = db.query(models.ParsedContent).filter(models.ParsedContent.file_id == file_id).first()
    return {"file_id": file_id, "parsed_content": parsed.content if parsed else {}}

@app.get("/files")
def list_files(db: Session = next(get_db())):
    files = db.query(models.File).all()
    return [{"id": f.id, "filename": f.filename, "status": f.status, "created_at": f.created_at.isoformat()} for f in files]

@app.delete("/files/{file_id}", status_code=204)
def delete_file(file_id: str, db: Session = next(get_db())):
    file = db.query(models.File).filter(models.File.id == file_id).first()
    if not file:
        raise HTTPException(404, "File not found")
    if os.path.exists(file.filepath):
        os.remove(file.filepath)
    db.query(models.ParsedContent).filter(models.ParsedContent.file_id == file_id).delete()
    db.delete(file)
    db.commit()
    return {}
