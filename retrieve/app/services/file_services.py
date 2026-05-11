import os
import uuid
from pathlib import Path

DATA_DIR = Path(os.getenv("RETRIEVE_DATA_DIR", "/data"))
MAX_FILE_SIZE_MB = int(os.getenv("RETRIEVE_MAX_FILE_SIZE_MB", "100"))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

save_file(request: ):


get_files():


delete_files():
