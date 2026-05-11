from enum import Enum
from datetime import datetime

from pydantic import BaseModel


class Category(str,Enum):
    ORIGINALS = "originals"
    PARSES = "parses"
    ARTIFACTS = "artifacts"

class Status(str,Enum):
    PENDING = "pending"
    DONE = "done"
    FAILED = "failed"



class FileUploadResponse(BaseModel):
    file_name: str
    file_size: int
    file_path: str
    content_type: str
    stored_at: datetime
    status: Status

class FileDeleteResponse(BaseModel):
    file_name: str
    file_path: str
    deleted_at: datetime
    status: Status

