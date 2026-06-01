from enum import Enum
from pydantic import BaseModel, ConfigDict


class Status(str,Enum):
    DONE = "done"
    FAILED = "failed"


class FileExtension(str,Enum):
    PDF = "pdf"
    PNG = "png"
    JPEG = "jpeg"

class Device(str,Enum):
    AUTO = "auto"
    GPU = "gpu"
    CPU = "cpu"

class OutputFormat(str,Enum):
    MARKDOWN = "markdown"
    JSON = "json"
    BOTH = "both"


class ExtractResponse(BaseModel):
   status: Status
   content_markdown: str | None = None 
   content_json: dict | None = None
   metadata: dict | None = None 
   processing_time_ms: float
   device_used: Device


class ExtractRequest(BaseModel):
    doc_id: int | None = None
    device: Device | None = None
    output_format: OutputFormat | None = None