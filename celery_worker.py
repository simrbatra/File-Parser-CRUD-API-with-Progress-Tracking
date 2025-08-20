from celery import Celery
from database import SessionLocal
from models import File, ParsedContent, FileStatus
import time
import csv
import json
from sqlalchemy.orm import Session

celery_app = Celery(
    "worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

@celery_app.task(bind=True)
def parse_file_task(self, file_id: str):
    db: Session = SessionLocal()
    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        return

    # Update status: processing
    file.status = FileStatus.processing
    file.progress = 0
    db.commit()

    parsed_data = []

    try:
        # For demonstration, only CSV parsing
        with open(file.filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            total = len(rows)
            chunk_size = max(1, total // 10)
            for i in range(0, total, chunk_size):
                chunk = rows[i:i+chunk_size]
                parsed_data.extend(chunk)
                # Update progress
                file.progress = min(100, int((i + chunk_size) / total * 100))
                db.commit()
                time.sleep(1)  # simulate delay

        # Save parsed data
        parsed_content = db.query(ParsedContent).filter(ParsedContent.file_id == file_id).first()
        if not parsed_content:
            parsed_content = ParsedContent(id=file_id, file_id=file_id, content=json.dumps(parsed_data))
            db.add(parsed_content)
        else:
            parsed_content.content = json.dumps(parsed_data)
        file.status = FileStatus.ready
        file.progress = 100
        db.commit()
    except Exception as e:
        file.status = FileStatus.failed
        file.progress = 0
        db.commit()
    finally:
        db.close()
