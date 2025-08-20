from sqlalchemy import Column, String, Integer, DateTime, Text, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()

class FileStatus(str, enum.Enum):
    uploading = "uploading"
    processing = "processing"
    ready = "ready"
    failed = "failed"

class File(Base):
    __tablename__ = "files"
    id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    status = Column(Enum(FileStatus), nullable=False)
    progress = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)
    filepath = Column(String, nullable=False)
    parsed_content = relationship("ParsedContent", back_populates="file", uselist=False, cascade="all, delete")

class ParsedContent(Base):
    __tablename__ = "parsed_content"
    id = Column(String, primary_key=True)
    file_id = Column(String, ForeignKey("files.id", ondelete="CASCADE"))
    content = Column(Text)
    file = relationship("File", back_populates="parsed_content")
