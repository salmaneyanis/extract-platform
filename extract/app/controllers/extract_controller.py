"""
Controller HTTP du service Extract (Docling).

POST /extract :
  - reçoit un fichier + paramètres (engine, profile, device, output_format)
  - route vers le moteur Docling choisi (classic ou vlm)
  - retourne le markdown généré
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.schemas.extract_schemas import ExtractResponse, Engine, Device, Profile, OutputFormat
from app.services.pipeline_service import extract_document

router = APIRouter(prefix="/extract", tags=["extract"])


def _normalize_device(device: str) -> str:
    """Accepte 'cuda' comme alias de 'gpu' (tolérance frontend)."""
    device = (device or "auto").lower()
    if device == "cuda":
        device = "gpu"
    return device


@router.post("", status_code=200, response_model=ExtractResponse)
async def extract(
    file: UploadFile = File(...),
    engine: str = Form(default="vlm"),
    profile: str = Form(default="balanced"),
    device: str = Form(default="auto"),
    output_format: str = Form(default="markdown"),
):
    """Extrait un document avec Docling (moteur classic ou vlm)."""
    device = _normalize_device(device)
    try:
        engine_enum = Engine(engine.lower())
        device_enum = Device(device)
        profile_enum = Profile(profile.lower())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Valeur invalide : {e}")

    file_content = await file.read()
    if not file_content:
        raise HTTPException(status_code=400, detail="Fichier vide")

    result = await extract_document(
        file_content=file_content,
        filename=file.filename or "document.pdf",
        engine=engine_enum.value,
        profile=profile_enum.value,
        device=device_enum.value,
    )

    if result["status"] == "failed":
        detail = result.get("metadata", {}).get("error", "Extraction échouée")
        raise HTTPException(status_code=500, detail=detail)

    return ExtractResponse(**result)
