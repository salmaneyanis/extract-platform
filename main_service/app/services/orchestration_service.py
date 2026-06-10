import httpx
import time
import logging

logger = logging.getLogger(__name__)

async def upload_document(file_content, file_name):
    async with httpx.AsyncClient(timeout=300) as client:
        resp = await client.post(
            "http://store_data:8003/documents",
            json={"file_name": file_name, "category": "originals"}
        )
        data = resp.json()
        doc_id = data["doc_id"]

        files = {"uploaded_file": (file_name, file_content)}
        data = {"category": "originals", "doc_id": str(doc_id)}
        resp = await client.post(
            "http://retrieve:8002/files",
            files=files,
            data=data
        )

        data = resp.json()
        file_path = data["file_path"]

        # Update document with file_path
        resp = await client.patch(
            f"http://store_data:8003/documents/{doc_id}",
            json={"file_path": file_path}
        )
        resp.raise_for_status()

    return {"doc_id": doc_id, "status": "uploaded", "file_path": file_path}


async def extract_document(file_path, output_format, device):
    try:
        async with httpx.AsyncClient(timeout=300) as client:
            resp = await client.get(
                f"http://retrieve:8002/files/{file_path}"
            )
            resp.raise_for_status()
            file_content = resp.content

            files = {"file": ("document", file_content)}
            resp = await client.post(
                "http://extract:8001/extract",
                files=files,
                data={
                    "output_format": output_format,
                    "device": device,
                },
            )
            resp.raise_for_status()
            extract_data = resp.json()
            logger.info(f"Extract success: {extract_data}")
            return extract_data
    except Exception as e:
        logger.error(f"Extract failed: {e}", exc_info=True)
        raise


async def save_parse(doc_id, content_markdown, content_json, output_format):
    try:
        async with httpx.AsyncClient(timeout=300) as client:
            resp = await client.post(
                "http://store_data:8003/parses",
                json={
                    "doc_id": doc_id,
                    "representation_type": output_format,
                    "content_json": content_json,
                    "content_text": content_markdown,
                }
            )
            resp.raise_for_status()
            parse_data = resp.json()
            logger.info(f"Parse saved: {parse_data}")
            return parse_data
    except Exception as e:
        logger.error(f"Save parse failed: {e}", exc_info=True)
        raise


async def create_job(doc_id):
    async with httpx.AsyncClient(timeout=300) as client:
        resp = await client.post(
            "http://store_data:8003/jobs",
            json={
                "doc_id": doc_id,
                "job_type": "extract",
            }
        )
        resp.raise_for_status()
    return resp.json()


async def update_job(job_id, status, result=None):
    async with httpx.AsyncClient(timeout=300) as client:
        resp = await client.patch(
            f"http://store_data:8003/jobs/{job_id}",
            json={
                "status": status,
                "result": result,
            }
        )
        resp.raise_for_status()
    return resp.json()


async def extract_and_save(
    doc_id: int,
    output_format: str = "markdown",
    device: str = "auto",
    profile: str = "balanced",
):
    """Extract document déjà uploadé, save parse, create job."""
    try:
        async with httpx.AsyncClient(timeout=300) as client:
            resp = await client.get(f"http://store_data:8003/documents/{doc_id}")
            resp.raise_for_status()
            doc_data = resp.json()
            file_path = doc_data.get("file_path")

            if not file_path:
                raise ValueError(f"Document {doc_id} has no file_path")

        extract_result = await extract_document(file_path, output_format, device)
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
        logger.error(f"Extract and save failed: {e}", exc_info=True)
        raise


async def process_document(
    file_content: bytes,
    file_name: str,
    profile: str = "balanced",
    device: str = "auto",
    output_format: str = "markdown",
):
    start_time = time.time()
    doc_id = None
    job_id = None

    try:
        upload_result = await upload_document(file_content, file_name)
        doc_id = upload_result["doc_id"]
        file_path = upload_result["file_path"]

        job_result = await create_job(doc_id)
        job_id = job_result["job_id"]

        extract_result = await extract_document(
            file_path, output_format, device
        )

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

        return {
            "job_id": job_id,
            "doc_id": doc_id,
            "status": "done",
            "processing_time_ms": (time.time() - start_time) * 1000,
        }

    except Exception as e:
        logger.error(f"Process failed: {e}", exc_info=True)
        if job_id:
            await update_job(job_id, "failed", {"error": str(e)})
        return {
            "job_id": job_id,
            "doc_id": doc_id,
            "status": "failed",
            "error": str(e),
            "processing_time_ms": (time.time() - start_time) * 1000,
        }
