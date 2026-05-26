from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Text,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base
from app.schemas.document_schemas import Category, Status


class Document(Base):
    __tablename__ = "documents"
    
    doc_id = Column(BigInteger, primary_key=True, autoincrement=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=True)
    file_size = Column(BigInteger, nullable=True)
    content_type = Column(String(100), nullable=True)
    category = Column(SQLEnum(Category), nullable=False)
    status = Column(SQLEnum(Status), nullable=False, default=Status.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    parses = relationship("DocumentParse", back_populates="document", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="document", cascade="all, delete-orphan")


class DocumentParse(Base):
    __tablename__ = "document_parses"
    
    parse_id = Column(BigInteger, primary_key=True, autoincrement=True)
    doc_id = Column(BigInteger, ForeignKey("documents.doc_id", ondelete="CASCADE"), nullable=False)
    representation_type = Column(String(50), nullable=False)
    content_json = Column(JSONB, nullable=True)
    content_text = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    document = relationship("Document", back_populates="parses")


class Job(Base):
    __tablename__ = "jobs"
    
    job_id = Column(BigInteger, primary_key=True, autoincrement=True)
    doc_id = Column(BigInteger, ForeignKey("documents.doc_id", ondelete="CASCADE"), nullable=True)
    job_type = Column(String(50), nullable=False)
    status = Column(SQLEnum(Status), nullable=False, default=Status.PENDING)
    result = Column(JSONB, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    
    document = relationship("Document", back_populates="jobs")