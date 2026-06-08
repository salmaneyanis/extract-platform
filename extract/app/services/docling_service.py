import logging
from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    EasyOcrOptions,
    PdfPipelineOptions,
    TableFormerMode,
    PdfBackend,
)
from docling_core.types.doc import ImageRefMode
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc import ImageRefMode
import copy

from app.config import PROFILES
from app.schemas.extract_schemas import (
    ExtractProfile,
    OcrOptions,
    TableOptions,
    ImageOptions,
)



def merge_options(
    profile: ExtractProfile,
    ocr: OcrOptions | None = None,
    tables: TableOptions | None = None,
    images: ImageOptions | None = None,
) -> dict:
    """
    Fusionne la configuration d'un profil avec les overrides utilisateur.
    
    Args:
        profile: Profil de base (FAST, BALANCED, ACCURATE, SCAN_OCR)
        ocr: Overrides OCR optionnels
        tables: Overrides tables optionnels
        images: Overrides images optionnels
    
    Returns:
        Dict avec la config finale fusionnée :
        {
            "ocr": {...},
            "tables": {...},
            "images": {...},
        }
    """
    # 1. Copier la config du profil (sans modifier l'original)
    config = copy.deepcopy(PROFILES[profile])
    
    # 2. Appliquer les overrides OCR si fournis
    if ocr is not None:
        ocr_overrides = ocr.model_dump(exclude_none=True)
        config["ocr"].update(ocr_overrides)
    
    # 3. Appliquer les overrides tables si fournis
    if tables is not None:
        tables_overrides = tables.model_dump(exclude_none=True)
        config["tables"].update(tables_overrides)
    
    # 4. Appliquer les overrides images si fournis
    if images is not None:
        images_overrides = images.model_dump(exclude_none=True)
        config["images"].update(images_overrides)
    
    return config


def build_pipeline_options_ocr(config: dict):

    pipeline_options = PdfPipelineOptions()
    pipeline_options.backend = PdfBackend.DLPARSE_V2

    # ocr
    pipeline_options.do_ocr = config["ocr"]["do_ocr"]
    pipeline_options.ocr_options.lang = config["ocr"]["lang"]
    pipeline_options.ocr_options.force_full_page_ocr = config["ocr"]["force_full_page_ocr"]

    # device/gpu — use accelerator_options, not ocr_options.use_gpu
    if config["ocr"]["use_gpu"]:
        pipeline_options.accelerator_options.device = "cuda"
    else:
        pipeline_options.accelerator_options.device = "cpu"

    # tables
    pipeline_options.do_table_structure = config["tables"]["do_table_structure"]
    pipeline_options.table_structure_options.do_cell_matching = config["tables"]["do_cell_matching"]

    table_mode = config["tables"]["table_mode"]
    if isinstance(table_mode, str):
        table_mode = TableFormerMode(table_mode)
    elif hasattr(table_mode, 'value'):
        table_mode = TableFormerMode(table_mode.value)
    pipeline_options.table_structure_options.mode = table_mode

    # images
    pipeline_options.generate_picture_images = config["images"]["generate_picture_images"]
    pipeline_options.generate_table_images = config["images"]["generate_table_images"]
    pipeline_options.images_scale = config["images"]["images_scale"]

    return pipeline_options



