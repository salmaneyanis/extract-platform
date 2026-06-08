# config.py
import os
from pathlib import Path
from app.schemas.extract_schemas import ExtractProfile, TableMode


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

# == Profil Docling === 
PROFILES = {
    ExtractProfile.FAST: {
        "ocr": {
            "do_ocr": True,
            "lang": ["fr"],
            "force_full_page_ocr": False,
            "use_gpu": True,
        },
        "tables": {
            "do_table_structure": False,
            "table_mode":TableMode.FAST ,
            "do_cell_matching": False,
        },
        "images": {
            "generate_picture_images": False,
            "generate_table_images": False,
            "images_scale": 1.0
        }
    },
     ExtractProfile.BALANCED: {
        "ocr": {
            "do_ocr": True,
            "lang": ["fr"],
            "force_full_page_ocr": False,
            "use_gpu": True,
        },
        "tables": {
            "do_table_structure": False,
            "table_mode":TableMode.FAST,
            "do_cell_matching": False,
        },
        "images": {
            "generate_picture_images": False,
            "generate_table_images": False,
            "images_scale": 1.0
        }
    },
     ExtractProfile.ACCURATE: {
        "ocr": {
            "do_ocr": True,
            "lang": ["fr"],
            "force_full_page_ocr": True,
            "use_gpu": True,
        },
        "tables": {
            "do_table_structure": True,
            "table_mode":TableMode.ACCURATE,
            "do_cell_matching": True,
        },
        "images": {
            "generate_picture_images": False,
            "generate_table_images": False,
            "images_scale": 2.0
        }


    }

}



