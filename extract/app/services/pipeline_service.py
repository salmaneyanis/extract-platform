"""
Pipeline service : orchestration de l'extraction Docling (classic ou vlm).

Exécute l'inférence Docling (synchrone, bloquante) dans un ThreadPoolExecutor
pour ne pas bloquer l'event loop FastAPI, et mappe le résultat au format
attendu par le controller.
"""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

from app.config import EXTRACT_WORKERS, DEFAULT_ENGINE
from app.schemas.extract_schemas import Device, Engine, Profile
from app.services.docling_service import parse_document, ParseError

logger = logging.getLogger(__name__)

_executor = ThreadPoolExecutor(max_workers=EXTRACT_WORKERS)


async def extract_document(
    file_content: bytes,
    filename: str = "document.pdf",
    engine: str = None,
    profile: str = "balanced",
    device: str = "auto",
) -> dict:
    """
    Extrait un document avec Docling, sans bloquer l'event loop.

    engine : "classic" ou "vlm" (défaut : DEFAULT_ENGINE)
    profile : fast/balanced/accurate (utilisé par le moteur classic uniquement)
    device : auto/gpu/cpu
    """
    engine = (engine or DEFAULT_ENGINE)
    if isinstance(engine, Engine):
        engine = engine.value
    if isinstance(profile, Profile):
        profile = profile.value
    if isinstance(device, Device):
        device = device.value

    loop = asyncio.get_event_loop()

    try:
        result = await loop.run_in_executor(
            _executor,
            parse_document,
            file_content,
            filename,
            engine,
            profile,
            device,
        )
        return result

    except ParseError as e:
        logger.error(f"Extraction échouée : {e}")
        return {
            "status": "failed",
            "content_markdown": None,
            "content_json": None,
            "metadata": {"error": str(e), "engine": engine},
            "processing_time_ms": 0.0,
            "device_used": device,
        }
    except Exception as e:
        logger.error(f"Erreur inattendue : {e}", exc_info=True)
        return {
            "status": "failed",
            "content_markdown": None,
            "content_json": None,
            "metadata": {"error": str(e), "engine": engine},
            "processing_time_ms": 0.0,
            "device_used": device,
        }
