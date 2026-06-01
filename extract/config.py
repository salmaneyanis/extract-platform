# config.py
import os
from pathlib import Path

# === Workers pour ThreadPoolExecutor ===
CPU_WORKERS = int(os.getenv("EXTRACT_CPU_WORKERS", "4"))
GPU_WORKERS = int(os.getenv("EXTRACT_GPU_WORKERS", "1"))

# === Device par défaut ===
DEFAULT_DEVICE = os.getenv("EXTRACT_DEFAULT_DEVICE", "auto")

# === GPU disponible ou pas ===
GPU_AVAILABLE = os.getenv("EXTRACT_GPU_AVAILABLE", "false").lower() == "true"

# === Limites ===
MAX_FILE_SIZE_MB = int(os.getenv("EXTRACT_MAX_FILE_SIZE_MB", "100"))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# === Timeout (en secondes) ===
PARSE_TIMEOUT_SECONDS = int(os.getenv("EXTRACT_TIMEOUT_SECONDS", "300"))