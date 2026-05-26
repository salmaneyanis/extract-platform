from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB 
from app.database import Base
from app.schemas.document_schemas import Category, Status


from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, LargeBinary
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base
from app.schemas.document_schemas import Category, Status


class Metadata(Base):
    __tablename__ = "metadata"

    metadata_id = Column(Integer, primary_key=True)
    content = Column(LargeBinary, nullable=False)


class Document_Parse(Base):
    __tablename__ = "document_parse"

    doc_id = Column(Integer, ForeignKey("metadata.metadata_id", ondelete="CASCADE"), primary_key=True)
    representation_type = Column(String, nullable=True)
    content = Column(LargeBinary, nullable=False)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)


class Jobs(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)
    file_path = Column(String, nullable=True)
    status = Column(Enum(Status), default=Status.PENDING, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Document(Base):
    __tablename__ = "documents"

    doc_id = Column(Integer, ForeignKey("document_parse.doc_id", ondelete="CASCADE"), primary_key=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), primary_key=True)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)
    content_type = Column(String, nullable=True)
    category = Column(Enum(Category), nullable=False)
    status = Column(Enum(Status), default=Status.PENDING, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)