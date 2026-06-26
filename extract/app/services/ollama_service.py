import logging
import json
import requests
from app.schemas.extract_schemas import OutputFormat

logger = logging.getLogger(__name__)

OLLAMA_API = "http://localhost:11434/api/generate"


def extract_with_nu_extract(
    file_content: bytes,
    output_format: OutputFormat = OutputFormat.MARKDOWN,
) -> dict:
    """
    Extract using Ollama nu-extract model.
    nu-extract is optimized for structured data extraction.
    """
    try:
        import tempfile
        from pathlib import Path
        import base64

        # Save temp file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(file_content)
            tmp_path = Path(tmp.name)

        # For now, convert PDF to text first (simplified approach)
        # In production, would use pdfplumber or similar to extract text
        try:
            import pdfplumber
            with pdfplumber.open(tmp_path) as pdf:
                text_content = "\n".join([page.extract_text() or "" for page in pdf.pages])
        except ImportError:
            # Fallback: just use extracted text from Docling
            from docling.document_converter import DocumentConverter
            converter = DocumentConverter()
            doc = converter.convert(tmp_path, raises_on_error=False)
            text_content = doc.document.export_to_markdown()

        tmp_path.unlink()

        # Call Ollama nu-extract
        prompt = f"""Extract structured data from the following text:

{text_content}

Return the extracted data as JSON."""

        response = requests.post(
            OLLAMA_API,
            json={
                "model": "nuextract:3.8b",
                "prompt": prompt,
                "stream": False,
                "temperature": 0.3,
            },
            timeout=300
        )
        response.raise_for_status()

        result_text = response.json().get("response", "")

        # Parse JSON from response
        try:
            import re
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                content_json = json.loads(json_match.group())
            else:
                content_json = {"raw": result_text}
        except:
            content_json = {"raw": result_text}

        result = {
            "content_markdown": text_content,
            "content_json": content_json if output_format in (OutputFormat.JSON, OutputFormat.BOTH) else None,
        }

        return result

    except Exception as e:
        logger.error(f"Ollama nu-extract failed: {e}", exc_info=True)
        raise
