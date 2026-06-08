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



class ExtractProfile(str,Enum):
    FAST = "fast"
    BALANCED = "balanced"
    ACCURATE = "accurate"
    SCAN_OCR = "scan_ocr"


class TableMode(str,Enum):
    FAST = "fast"
    ACCURATE = "accurate"

class TableOptions(BaseModel):
    do_table_structure: bool | None = None
    table_mode: TableMode | None = None
    do_cell_matching: bool | None = None

class OcrOptions(BaseModel):
    do_ocr: bool | None = None
    lang: list[str] | None = None
    force_full_page_ocr: bool | None = None
    use_gpu: bool | None = None

class ImageOptions(BaseModel):
    generate_picture_images: bool | None = None
    generate_table_images: bool | None = None
    images_scale: float | None = None  


class ExtractRequest(BaseModel):
    doc_id: int | None = None
    device: Device = Device.AUTO
    output_format: OutputFormat = OutputFormat.MARKDOWN
    profile: ExtractProfile = ExtractProfile.BALANCED
    ocr: OcrOptions | None = None
    images: ImageOptions | None = None
    tables: TableOptions | None = None
    
    
