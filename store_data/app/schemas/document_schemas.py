from enum import Enum
from datetime import datetime
from pydantic import BaseModel, field_validator, ConfigDict



class Category(str,Enum):
    ORIGINALS = "originals"
    PARSES = "parses"
    ARTIFACTS = "artifacts"

class Status(str,Enum):
    DONE = "done"
    FAILED = "failed"
    PROCESSING = "processing"
    PENDING = "pending"
    STORED = "stored"

class DocumentCreate(BaseModel):
    file_name: str 
    category: Category 

class DocumentUpdate(BaseModel):
    file_path: str | None = None
    file_size: int | None = None
    content_type: str | None = None
    status: Status | None = None


class DocumentResponse(BaseModel):
    doc_id: int
    file_name: str
    file_path: str | None             
    file_size: int | None             
    content_type: str | None          
    category: Category
    status: Status
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class DocumentParseCreate(BaseModel):
    doc_id: int

class DocumentParseResponse(BaseModel):
    parse_id: int
    doc_id: int 
    representation_type: str | None 
    content_json: dict | None
    content_text: str | None
    created_at: datetime



class JobCreate(BaseModel):
    doc_id: int 
    job_type: str

class JobUpdate(BaseModel): 
    file_path: str | None = None
    job_type: str | None = None


class JobResponse(BaseModel):
    job_id: int
    job_type: str
    status: Status
    result: dict
    error: str
    created_at: datetime
    started_at: datetime
    finished_at: datetime


