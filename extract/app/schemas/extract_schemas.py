"""
Schemas du service Extract (Docling : classic + vlm).
"""

from enum import Enum
from pydantic import BaseModel


class Status(str, Enum):
    DONE = "done"
    FAILED = "failed"


class Engine(str, Enum):
    CLASSIC = "classic"   # pipeline OCR Docling (profils)
    VLM = "vlm"           # VLM Nanonets via Docling


class Device(str, Enum):
    AUTO = "auto"
    GPU = "gpu"
    CPU = "cpu"


class Profile(str, Enum):
    FAST = "fast"
    BALANCED = "balanced"
    ACCURATE = "accurate"


class OutputFormat(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"
    BOTH = "both"


class ExtractResponse(BaseModel):
    status: Status
    content_markdown: str | None = None
    content_json: dict | None = None
    metadata: dict | None = None
    processing_time_ms: float
    device_used: str | None = None
