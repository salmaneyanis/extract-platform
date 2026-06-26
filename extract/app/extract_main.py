"""
Point d'entrée du service Extract (Docling : classic + vlm).

Au démarrage, on précharge le converter du moteur par défaut. Avec Docling,
créer le converter est rapide ; le modèle VLM se charge réellement à la
première extraction.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import DEFAULT_ENGINE
from app.services.docling_service import preload, is_ready, get_device

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Démarrage du service Extract (Docling, moteur par défaut={DEFAULT_ENGINE})...")
    try:
        preload(DEFAULT_ENGINE)
        logger.info("Converter prêt")
    except Exception as e:
        logger.error(f"Préchargement échoué : {e}")
    yield


app = FastAPI(title="Extract Service (Docling)", lifespan=lifespan)

from app.controllers.extract_controller import router as extract_router  # noqa: E402

app.include_router(extract_router)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "extract",
        "engine_default": DEFAULT_ENGINE,
        "ready": is_ready(),
        "device": get_device(),
    }


@app.get("/")
async def root():
    return {"message": "Extract Service (Docling) is running"}
