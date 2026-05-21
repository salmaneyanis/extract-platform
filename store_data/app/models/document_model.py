from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB 
from app.database import Base
from app.schemas.document_schemas import Category, Status


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)
    content_type = Column(String, nullable=True)
    category = Column(Enum(Category), nullable=False)
    status = Column(Enum(Status), default=Status.PENDING, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)






