from pydantic import BaseModel, ConfigDict
from enum import Enum


class Status(str, Enum):
    DONE = "done"
    FAILED = "failed"
    PROCESSING = "processing"
    PENDING = "pending"


class ProcessResponse(BaseModel):
    job_id: int
    doc_id: int
    status: Status
    processing_time_ms: float | None = None

    model_config = ConfigDict(from_attributes=True)


class ProcessRequest(BaseModel):
    profile: str = "balanced"
    device: str = "auto"
    output_format: str = "markdown"
