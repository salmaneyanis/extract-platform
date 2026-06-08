import logging
import json
import time
import tempfile
from pathlib import Path

from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat

from app.schemas.extract_schemas import OutputFormat, Device
from app.services.docling_service import merge_options, build_pipeline_options_ocr

logger = logging.getLogger(__name__)


def extract_document(
    file_content: bytes,
    profile,
    output_format: OutputFormat = OutputFormat.MARKDOWN,
    device: Device = Device.AUTO,
    ocr=None,
    images=None,
    tables=None,
):
    """
    Convert PDF/image to markdown/json.
    MUST BE def, NOT async def — avoids blocking event loop.
    """
    start_time = time.time()

    try:
        converter = DocumentConverter()

        config = merge_options(profile, ocr, tables, images)

        pdf_option = converter.format_to_options[InputFormat.PDF]
        opts = pdf_option.pipeline_options

        opts.do_ocr = config["ocr"]["do_ocr"]
        opts.ocr_options.lang = config["ocr"]["lang"]
        opts.ocr_options.force_full_page_ocr = config["ocr"]["force_full_page_ocr"]

        if config["ocr"]["use_gpu"]:
            opts.accelerator_options.device = "cuda"
        else:
            opts.accelerator_options.device = "cpu"

        opts.do_table_structure = config["tables"]["do_table_structure"]
        opts.table_structure_options.do_cell_matching = config["tables"]["do_cell_matching"]

        from docling.datamodel.pipeline_options import TableFormerMode
        table_mode = config["tables"]["table_mode"]
        if isinstance(table_mode, str):
            table_mode = TableFormerMode(table_mode)
        elif hasattr(table_mode, 'value'):
            table_mode = TableFormerMode(table_mode.value)
        opts.table_structure_options.mode = table_mode

        opts.generate_picture_images = config["images"]["generate_picture_images"]
        opts.generate_table_images = config["images"]["generate_table_images"]
        opts.images_scale = config["images"]["images_scale"]

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(file_content)
            tmp_path = Path(tmp.name)

        doc = converter.convert(tmp_path, raises_on_error=False)
        tmp_path.unlink()

        result = {}

        if output_format in (OutputFormat.MARKDOWN, OutputFormat.BOTH):
            result["content_markdown"] = doc.document.export_to_markdown()

        if output_format in (OutputFormat.JSON, OutputFormat.BOTH):
            result["content_json"] = json.loads(doc.document.export_to_json())

        processing_time_ms = (time.time() - start_time) * 1000

        return {
            "status": "done",
            "content_markdown": result.get("content_markdown"),
            "content_json": result.get("content_json"),
            "metadata": {
                "pages": len(doc.document.pages),
                "model": str(doc.model_name) if hasattr(doc, "model_name") else "unknown",
            },
            "processing_time_ms": processing_time_ms,
            "device_used": device.value if isinstance(device, Device) else device,
        }

    except Exception as e:
        logger.error(f"Extract failed: {e}", exc_info=True)
        return {
            "status": "failed",
            "content_markdown": None,
            "content_json": None,
            "metadata": {"error": str(e)},
            "processing_time_ms": (time.time() - start_time) * 1000,
            "device_used": device.value if isinstance(device, Device) else device,
        }
