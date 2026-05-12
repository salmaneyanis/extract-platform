import os
import uuid
from pathlib import Path
import FileUploadResponse from "../schemas/file_schemas.py"

DATA_DIR = Path(os.getenv("RETRIEVE_DATA_DIR", "/data"))
MAX_FILE_SIZE_MB = int(os.getenv("RETRIEVE_MAX_FILE_SIZE_MB", "100"))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

async def save_file(content: bytes, filename: str, category: Category) -> FileUploadResponse:
   



async def get_files():


async def delete_files():
