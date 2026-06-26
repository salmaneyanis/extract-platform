"""
Service Docling : moteur d'extraction unifié.

Deux modes au choix (paramètre `engine`) :

  - "classic" : pipeline OCR traditionnel de Docling (EasyOCR + analyse de layout
    + TableFormer). Les profils fast/balanced/accurate configurent ce pipeline.
    Rapide, léger, idéal pour des PDF déjà textuels ou peu complexes.

  - "vlm" : VlmPipeline de Docling avec un modèle vision-langage (Nanonets-OCR2-3B,
    ~4B paramètres, spécialisé documents financiers). Le VLM "regarde" chaque page
    et génère le markdown de bout en bout. Plus puissant sur les scans et documents
    complexes, mais plus lourd (GPU recommandé).

Les deux modes retournent EXACTEMENT le même format de dict, pour que le reste de
la chaîne (pipeline_service, controller) ne voie pas la différence.

Les converters Docling sont créés une seule fois (singleton, lazy loading) :
chaque moteur ne se charge que la première fois qu'on l'utilise.
"""

import io
import logging
import threading
import time

from docling.datamodel.base_models import InputFormat, DocumentStream
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    VlmPipelineOptions,
    TableFormerMode,
)
from docling.datamodel.accelerator_options import AcceleratorOptions, AcceleratorDevice
from docling.pipeline.vlm_pipeline import VlmPipeline
from docling.datamodel import vlm_model_specs

from app.config import (
    VLM_MAX_NEW_TOKENS,
    DEFAULT_ENGINE,
)

logger = logging.getLogger(__name__)


# === Exceptions custom ===
class ModelLoadError(Exception):
    """Le moteur n'a pas pu être chargé/configuré."""
    pass


class ParseError(Exception):
    """Erreur pendant le parsing d'un document."""
    pass


# === Singletons des converters (lazy loading) ===
# On crée chaque converter une seule fois, à la première utilisation.
# _classic_converters : un converter par profil (fast/balanced/accurate).
# _vlm_converter : un seul converter VLM.
_classic_converters = {}
_vlm_converter = None
_device = None
_lock = threading.Lock()
_inference_lock = threading.Lock()  # Docling/torch : on sérialise les inférences GPU


def _resolve_accelerator(requested: str) -> AcceleratorDevice:
    """
    Résout le device Docling à partir de la demande ('auto', 'gpu', 'cpu').

    Docling gère lui-même la détection ; AUTO laisse Docling choisir.
    """
    requested = (requested or "auto").lower()
    if requested == "cpu":
        return AcceleratorDevice.CPU
    if requested == "gpu":
        return AcceleratorDevice.CUDA
    return AcceleratorDevice.AUTO


# ---------------------------------------------------------------------------
# Pipeline CLASSIQUE (OCR + TableFormer) — les profils s'appliquent ICI
# ---------------------------------------------------------------------------
def _build_classic_options(profile: str, device: str) -> PdfPipelineOptions:
    """
    Construit les options du pipeline classique selon le profil.

    fast     : pas d'OCR forcé, pas de structure de table → le plus rapide.
    balanced : OCR + structure de table en mode rapide → bon compromis.
    accurate : OCR + structure de table en mode précis + appariement cellules.
    """
    profile = (profile or "balanced").lower()
    opts = PdfPipelineOptions()
    opts.accelerator_options = AcceleratorOptions(device=_resolve_accelerator(device))

    if profile == "fast":
        opts.do_ocr = False
        opts.do_table_structure = False
    elif profile == "accurate":
        opts.do_ocr = True
        opts.do_table_structure = True
        opts.table_structure_options.mode = TableFormerMode.ACCURATE
        opts.table_structure_options.do_cell_matching = True
    else:  # balanced (défaut)
        opts.do_ocr = True
        opts.do_table_structure = True
        opts.table_structure_options.mode = TableFormerMode.FAST

    return opts


def _get_classic_converter(profile: str, device: str) -> DocumentConverter:
    """Retourne (en le créant si besoin) le converter classique pour ce profil."""
    global _classic_converters
    profile = (profile or "balanced").lower()
    key = f"{profile}:{device}"

    if key in _classic_converters:
        return _classic_converters[key]

    with _lock:
        if key in _classic_converters:
            return _classic_converters[key]

        logger.info(f"Création du converter Docling classique (profil={profile}, device={device})...")
        opts = _build_classic_options(profile, device)
        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=opts),
            }
        )
        _classic_converters[key] = converter
        logger.info("Converter classique prêt")
        return converter


# ---------------------------------------------------------------------------
# Pipeline VLM (Nanonets-OCR2-3B) — les profils sont IGNORÉS (VLM end-to-end)
# ---------------------------------------------------------------------------
def _get_vlm_converter(device: str) -> DocumentConverter:
    """Retourne (en le créant si besoin) le converter VLM. Singleton."""
    global _vlm_converter, _device

    if _vlm_converter is not None:
        return _vlm_converter

    with _lock:
        if _vlm_converter is not None:
            return _vlm_converter

        logger.info("Création du converter Docling VLM (Nanonets-OCR2-3B)...")
        start = time.time()

        # GraniteDocling : modèle natif Docling, excellent sur la structure/tableaux
        # Granite-Vision : fonctionne en local (Vision2Seq, compatible transformers 5.x)
        vlm_options = VlmPipelineOptions(
            vlm_options=vlm_model_specs.GRANITE_VISION_TRANSFORMERS,
        )

        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_cls=VlmPipeline,
                    pipeline_options=vlm_options,
                ),
            }
        )
        _vlm_converter = converter
        _device = device
        logger.info(f"Converter VLM prêt (config en {time.time() - start:.1f}s ; "
                    f"le modèle se chargera à la 1re extraction)")
        return converter


# ---------------------------------------------------------------------------
# Préchargement (optionnel, appelé au démarrage)
# ---------------------------------------------------------------------------
def preload(engine: str = None) -> None:
    """
    Précharge le converter du moteur par défaut au démarrage.

    Note : avec Docling, créer le converter est rapide ; le modèle VLM ne se
    télécharge/charge vraiment qu'à la première extraction. On force donc une
    petite extraction à blanc serait coûteux — on se contente de créer le
    converter ici.
    """
    engine = (engine or DEFAULT_ENGINE).lower()
    try:
        if engine == "vlm":
            _get_vlm_converter("auto")
        else:
            _get_classic_converter("balanced", "auto")
    except Exception as e:
        logger.error(f"Préchargement du moteur {engine} échoué : {e}")
        raise ModelLoadError(str(e)) from e


def is_ready() -> bool:
    """Indique si au moins un converter est prêt."""
    return _vlm_converter is not None or len(_classic_converters) > 0


def get_device() -> str:
    return _device or "auto"


# ---------------------------------------------------------------------------
# Parsing d'un document
# ---------------------------------------------------------------------------
def parse_document(
    file_content: bytes,
    filename: str,
    engine: str = None,
    profile: str = "balanced",
    requested_device: str = "auto",
) -> dict:
    """
    Parse un document avec Docling, selon le moteur choisi.

    Args:
        file_content : contenu binaire du fichier
        filename : nom du fichier
        engine : "classic" ou "vlm" (défaut : DEFAULT_ENGINE)
        profile : fast/balanced/accurate (utilisé uniquement par le moteur classic)
        requested_device : auto/gpu/cpu

    Returns:
        dict : status, content_markdown, content_json, metadata,
               processing_time_ms, device_used

    Raises:
        ParseError en cas d'échec.
    """
    start = time.time()
    engine = (engine or DEFAULT_ENGINE).lower()

    try:
        # Choisir le bon converter selon le moteur
        if engine == "vlm":
            converter = _get_vlm_converter(requested_device)
            engine_label = "vlm:ibm-granite/granite-vision-3.2-2b"
        else:
            converter = _get_classic_converter(profile, requested_device)
            engine_label = f"classic:{profile}"

        # Docling accepte un flux nommé (DocumentStream) à partir des bytes
        source = DocumentStream(name=filename or "document.pdf", stream=io.BytesIO(file_content))

        # L'inférence est sérialisée (un seul GPU, on évite les accès concurrents)
        with _inference_lock:
            logger.info(f"Extraction Docling ({engine_label}) de {filename}...")
            result = converter.convert(source)

        doc = result.document
        markdown = doc.export_to_markdown()

        processing_time_ms = (time.time() - start) * 1000

        return {
            "status": "done",
            "content_markdown": markdown,
            "content_json": None,
            "metadata": {
                "engine": engine,
                "engine_detail": engine_label,
                "profile": profile if engine == "classic" else None,
            },
            "processing_time_ms": processing_time_ms,
            "device_used": _device or requested_device,
        }

    except Exception as e:
        logger.error(f"Échec du parsing de {filename} : {e}", exc_info=True)
        raise ParseError(f"Erreur de parsing ({engine}) : {e}") from e
