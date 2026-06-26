"""
Service d'orchestration du main_service.

Le main_service est l'unique porte d'entrée externe. Il orchestre les appels
HTTP vers les microservices internes (store_data, retrieve, extract) via httpx.

Aucune logique métier lourde ici : uniquement de la coordination.
"""

import time
import logging

import httpx

logger = logging.getLogger(__name__)

# URLs internes (réseau Docker). Centralisées pour faciliter la maintenance.
STORE_URL = "http://store_data:8003"
RETRIEVE_URL = "http://retrieve:8002"
EXTRACT_URL = "http://extract:8001"

# Timeouts généreux : l'inférence Docling (VLM) sur GPU peut prendre plusieurs
# minutes pour un PDF multi-pages.
DEFAULT_TIMEOUT = httpx.Timeout(60.0, read=None, write=60.0, pool=60.0)


# ---------------------------------------------------------------------------
# Upload : crée l'entrée BDD, stocke le fichier, met à jour le file_path
# ---------------------------------------------------------------------------
async def upload_document(file_content: bytes, file_name: str) -> dict:
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        # 1. Créer l'entrée document en BDD
        resp = await client.post(
            f"{STORE_URL}/documents",
            json={"file_name": file_name, "category": "originals"},
        )
        resp.raise_for_status()
        doc_id = resp.json()["doc_id"]

        # 2. Stocker le fichier physique via retrieve
        files = {"uploaded_file": (file_name, file_content)}
        data = {"category": "originals", "doc_id": str(doc_id)}
        resp = await client.post(f"{RETRIEVE_URL}/files", files=files, data=data)
        resp.raise_for_status()
        file_path = resp.json()["file_path"]

        # 3. Mettre à jour le document avec le file_path et la taille
        resp = await client.patch(
            f"{STORE_URL}/documents/{doc_id}",
            json={"file_path": file_path, "file_size": len(file_content), "status": "stored"},
        )
        resp.raise_for_status()

    return {"doc_id": doc_id, "status": "uploaded", "file_path": file_path}


# ---------------------------------------------------------------------------
# Extraction : récupère le fichier, appelle extract (Docling)
# ---------------------------------------------------------------------------
async def extract_document(file_path: str, output_format: str, device: str, profile: str = "balanced", engine: str = "vlm") -> dict:
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        resp = await client.get(f"{RETRIEVE_URL}/files/{file_path}")
        resp.raise_for_status()
        file_content = resp.content

        files = {"file": ("document.pdf", file_content)}
        resp = await client.post(
            f"{EXTRACT_URL}/extract",
            files=files,
            data={"engine": engine, "profile": profile, "output_format": output_format, "device": device},
        )
        resp.raise_for_status()
        return resp.json()


# ---------------------------------------------------------------------------
# Persistance des résultats
# ---------------------------------------------------------------------------
async def save_parse(doc_id: int, content_markdown, content_json, output_format: str) -> dict:
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        resp = await client.post(
            f"{STORE_URL}/parses",
            json={
                "doc_id": doc_id,
                "representation_type": output_format,
                "content_json": content_json,
                "content_text": content_markdown,
            },
        )
        resp.raise_for_status()
        return resp.json()


async def create_job(doc_id: int) -> dict:
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        resp = await client.post(
            f"{STORE_URL}/jobs",
            json={"doc_id": doc_id, "job_type": "extract"},
        )
        resp.raise_for_status()
        return resp.json()


async def update_job(job_id: int, status: str, result=None) -> dict:
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        resp = await client.patch(
            f"{STORE_URL}/jobs/{job_id}",
            json={"status": status, "result": result},
        )
        resp.raise_for_status()
        return resp.json()


async def _set_document_status(doc_id: int, status: str) -> None:
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        await client.patch(f"{STORE_URL}/documents/{doc_id}", json={"status": status})


# ---------------------------------------------------------------------------
# Récupération fichier / parses pour un document
# ---------------------------------------------------------------------------
async def get_document_file(doc_id: int):
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        resp = await client.get(f"{STORE_URL}/documents/{doc_id}")
        resp.raise_for_status()
        doc_data = resp.json()
        file_path = doc_data.get("file_path")
        if not file_path:
            raise ValueError(f"Document {doc_id} sans file_path")

        resp = await client.get(f"{RETRIEVE_URL}/files/{file_path}")
        resp.raise_for_status()
        return resp.content, doc_data["file_name"]


async def get_document_parses(doc_id: int):
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        resp = await client.get(f"{STORE_URL}/parses", params={"doc_id": doc_id})
        resp.raise_for_status()
        return resp.json()


# ---------------------------------------------------------------------------
# Workflow complet : upload -> extract -> save
# ---------------------------------------------------------------------------
async def process_document(
    file_content: bytes,
    file_name: str,
    profile: str = "balanced",
    device: str = "auto",
    output_format: str = "markdown",
    engine: str = "vlm",
) -> dict:
    start_time = time.time()
    doc_id = None
    job_id = None

    try:
        upload_result = await upload_document(file_content, file_name)
        doc_id = upload_result["doc_id"]
        file_path = upload_result["file_path"]

        job_result = await create_job(doc_id)
        job_id = job_result["job_id"]

        await _set_document_status(doc_id, "processing")

        extract_result = await extract_document(file_path, output_format, device, profile, engine)

        parse_result = await save_parse(
            doc_id,
            extract_result.get("content_markdown"),
            extract_result.get("content_json"),
            output_format,
        )

        await update_job(
            job_id,
            "done",
            {
                "parse_id": parse_result["parse_id"],
                "processing_time_ms": (time.time() - start_time) * 1000,
            },
        )

        await _set_document_status(doc_id, "done")

        return {
            "job_id": job_id,
            "doc_id": doc_id,
            "status": "done",
            "processing_time_ms": (time.time() - start_time) * 1000,
        }

    except Exception as e:
        logger.error(f"Process échoué : {e}", exc_info=True)
        if job_id:
            try:
                await update_job(job_id, "failed", {"error": str(e)})
            except Exception:
                pass
        if doc_id:
            try:
                await _set_document_status(doc_id, "failed")
            except Exception:
                pass
        return {
            "job_id": job_id,
            "doc_id": doc_id,
            "status": "failed",
            "error": str(e),
            "processing_time_ms": (time.time() - start_time) * 1000,
        }


# ---------------------------------------------------------------------------
# Extraction d'un document déjà uploadé (workflow "à la carte")
# ---------------------------------------------------------------------------
async def extract_and_save(
    doc_id: int,
    output_format: str = "markdown",
    device: str = "auto",
    profile: str = "balanced",
    engine: str = "vlm",
) -> dict:
    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            resp = await client.get(f"{STORE_URL}/documents/{doc_id}")
            resp.raise_for_status()
            doc_data = resp.json()
            file_path = doc_data.get("file_path")
            if not file_path:
                raise ValueError(f"Document {doc_id} sans file_path")

        await _set_document_status(doc_id, "processing")

        extract_result = await extract_document(file_path, output_format, device, profile, engine)
        parse_result = await save_parse(
            doc_id,
            extract_result.get("content_markdown"),
            extract_result.get("content_json"),
            output_format,
        )
        job_result = await create_job(doc_id)
        job_id = job_result["job_id"]

        await update_job(
            job_id,
            "done",
            {
                "parse_id": parse_result["parse_id"],
                "processing_time_ms": extract_result.get("processing_time_ms"),
            },
        )

        await _set_document_status(doc_id, "done")

        return {
            "job_id": job_id,
            "doc_id": doc_id,
            "parse_id": parse_result["parse_id"],
            "status": "done",
            "content_markdown": extract_result.get("content_markdown"),
            "content_json": extract_result.get("content_json"),
            "metadata": extract_result.get("metadata"),
            "processing_time_ms": extract_result.get("processing_time_ms"),
            "device_used": extract_result.get("device_used"),
        }
    except Exception as e:
        logger.error(f"Extract and save échoué : {e}", exc_info=True)
        if doc_id:
            try:
                await _set_document_status(doc_id, "failed")
            except Exception:
                pass
        return {
            "doc_id": doc_id,
            "status": "failed",
            "error": str(e),
        }


# ---------------------------------------------------------------------------
# CRUD forwarding vers store_data
# ---------------------------------------------------------------------------
async def get_document(doc_id: int):
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        resp = await client.get(f"{STORE_URL}/documents/{doc_id}")
        resp.raise_for_status()
        return resp.json()


async def list_documents(skip: int = 0, limit: int = 100):
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        resp = await client.get(f"{STORE_URL}/documents", params={"skip": skip, "limit": limit})
        resp.raise_for_status()
        return resp.json()


async def update_document(doc_id: int, data: dict):
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        resp = await client.patch(f"{STORE_URL}/documents/{doc_id}", json=data)
        resp.raise_for_status()
        return resp.json()


async def delete_document(doc_id: int):
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        resp = await client.delete(f"{STORE_URL}/documents/{doc_id}")
        resp.raise_for_status()


async def get_parse(parse_id: int):
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        resp = await client.get(f"{STORE_URL}/parses/{parse_id}")
        resp.raise_for_status()
        return resp.json()


async def list_parses(skip: int = 0, limit: int = 100):
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        resp = await client.get(f"{STORE_URL}/parses", params={"skip": skip, "limit": limit})
        resp.raise_for_status()
        return resp.json()


async def delete_parse(parse_id: int):
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        resp = await client.delete(f"{STORE_URL}/parses/{parse_id}")
        resp.raise_for_status()


async def get_job(job_id: int):
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        resp = await client.get(f"{STORE_URL}/jobs/{job_id}")
        resp.raise_for_status()
        return resp.json()


async def list_jobs(skip: int = 0, limit: int = 100):
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        resp = await client.get(f"{STORE_URL}/jobs", params={"skip": skip, "limit": limit})
        resp.raise_for_status()
        return resp.json()


async def update_job_proxy(job_id: int, data: dict):
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        resp = await client.patch(f"{STORE_URL}/jobs/{job_id}", json=data)
        resp.raise_for_status()
        return resp.json()


async def delete_job(job_id: int):
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        resp = await client.delete(f"{STORE_URL}/jobs/{job_id}")
        resp.raise_for_status()
