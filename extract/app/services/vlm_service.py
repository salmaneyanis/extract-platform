import logging
import time
import torch
from pathlib import Path
import tempfile
from pdf2image import convert_from_path
from transformers import AutoModelForImageTextToText, AutoProcessor

logger = logging.getLogger(__name__)

MODEL_ID = "numind/NuExtract3-W4A16"
DPI = 150
MAX_NEW_TOKENS = 4096

_model = None
_processor = None


def load_vlm_model():
    global _model, _processor
    if _model is None:
        logger.info(f"Loading VLM model: {MODEL_ID}")
        _processor = AutoProcessor.from_pretrained(MODEL_ID, trust_remote_code=True)
        _model = AutoModelForImageTextToText.from_pretrained(
            MODEL_ID,
            dtype=torch.bfloat16,
            device_map="auto",
            trust_remote_code=True,
        ).eval()
        logger.info(f"VLM model loaded. VRAM: {torch.cuda.memory_allocated() / 1e9:.2f} Go")


def extract_with_vlm(file_content: bytes) -> dict:
    """
    Extract using HuggingFace NuExtract3-W4A16 vision-language model.
    Converts PDF to images, processes with VLM, returns markdown.
    """
    start_time = time.time()

    try:
        load_vlm_model()

        # Save temp file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(file_content)
            tmp_path = Path(tmp.name)

        # Convert PDF to images
        logger.info("Converting PDF to images...")
        pages = convert_from_path(str(tmp_path), dpi=DPI)
        logger.info(f"Converted {len(pages)} pages")

        tmp_path.unlink()

        # Process each page with VLM
        all_markdown = []
        for i, page in enumerate(pages):
            logger.info(f"Processing page {i + 1}/{len(pages)}")

            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": page},
                        {"type": "text", "text": "Convert this page to markdown. Extract all text, tables, and structured data."},
                    ],
                }
            ]

            inputs = _processor.apply_chat_template(
                messages,
                add_generation_prompt=True,
                tokenize=True,
                return_dict=True,
                return_tensors="pt",
            ).to(_model.device)

            with torch.inference_mode():
                output_ids = _model.generate(
                    **inputs,
                    max_new_tokens=MAX_NEW_TOKENS,
                    do_sample=False,
                )

            output_ids = output_ids[:, inputs.input_ids.shape[1]:]
            markdown = _processor.batch_decode(output_ids, skip_special_tokens=True)[0]
            all_markdown.append(markdown)

        full_markdown = "\n\n---\n\n".join(all_markdown)

        return {
            "content_markdown": full_markdown,
            "content_json": {
                "model": MODEL_ID,
                "pages": len(pages),
                "extraction_method": "vlm"
            }
        }

    except Exception as e:
        logger.error(f"VLM extraction failed: {e}", exc_info=True)
        raise
