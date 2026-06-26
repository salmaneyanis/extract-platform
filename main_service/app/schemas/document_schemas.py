from pydantic import BaseModel, ConfigDict
from enum import Enum
from datetime import datetime


class Status(str, Enum):
    DONE = "done"
    FAILED = "failed"
    PROCESSING = "processing"
    PENDING = "pending"


class ProcessResponse(BaseModel):
    doc_id: int
    status: Status
    message: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ProcessRequest(BaseModel):
    profile: str = "balanced"
    device: str = "auto"
    output_format: str = "markdown"


class UploadResponse(BaseModel):
    doc_id: int
    file_name: str
    file_size: int
    file_path: str
    category: str
    stored_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ExtractOnlyResponse(BaseModel):
    job_id: int
    doc_id: int
    parse_id: int
    status: Status
    content_markdown: str | None = None
    content_json: dict | None = None
    metadata: dict | None = None
    processing_time_ms: float
    device_used: str

    model_config = ConfigDict(from_attributes=True)


class DocumentUpdate(BaseModel):
    file_path: str | None = None
    file_size: int | None = None
    content_type: str | None = None
    status: str | None = None


class JobUpdate(BaseModel):
    status: Status | None = None
    result: dict | None = None
    error_message: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
