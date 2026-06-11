from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import FileResponse
from app.schemas.document_schemas import (
    ProcessResponse, Status, UploadResponse, ExtractOnlyResponse,
    DocumentUpdate
)
from app.services.orchestration_service import (
    process_document, upload_document, extract_and_save, get_document_file, get_document_parses,
    get_document, list_documents, update_document, delete_document,
    get_parse, list_parses, delete_parse,
    get_job, list_jobs, update_job_proxy, delete_job
)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", status_code=200, response_model=ProcessResponse)
async def process(
    file: UploadFile = File(...),
    profile: str = Form(default="balanced"),
    device: str = Form(default="auto"),
    output_format: str = Form(default="markdown"),
):
    """Process document: upload → extract → save."""
    try:
        file_content = await file.read()
        result = await process_document(
            file_content=file_content,
            file_name=file.filename,
            profile=profile,
            device=device,
            output_format=output_format,
        )

        if result["status"] == "failed":
            raise HTTPException(status_code=400, detail=result.get("error"))

        return ProcessResponse(
            job_id=result["job_id"],
            doc_id=result["doc_id"],
            status=Status(result["status"]),
            processing_time_ms=result.get("processing_time_ms"),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload", status_code=201, response_model=UploadResponse)
async def upload(
    file: UploadFile = File(...),
):
    """Upload fichier seulement."""
    try:
        file_content = await file.read()
        result = await upload_document(file_content, file.filename)
        return UploadResponse(
            doc_id=result["doc_id"],
            file_name=file.filename,
            file_size=len(file_content),
            file_path=result["file_path"],
            category="originals",
            stored_at=result.get("stored_at"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{doc_id}/extract", status_code=200, response_model=ExtractOnlyResponse)
async def extract_route(
    doc_id: int,
    profile: str = Form(default="balanced"),
    device: str = Form(default="auto"),
    output_format: str = Form(default="markdown"),
):
    """Extract document déjà uploadé."""
    try:
        result = await extract_and_save(
            doc_id=doc_id,
            output_format=output_format,
            device=device,
            profile=profile,
        )

        return ExtractOnlyResponse(
            job_id=result["job_id"],
            doc_id=result["doc_id"],
            parse_id=result["parse_id"],
            status=Status(result["status"]),
            content_markdown=result.get("content_markdown"),
            content_json=result.get("content_json"),
            metadata=result.get("metadata"),
            processing_time_ms=result.get("processing_time_ms"),
            device_used=result.get("device_used"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{doc_id}/file", status_code=200)
async def get_file(doc_id: int):
    """Download file from retrieve for document."""
    try:
        file_content, file_name = await get_document_file(doc_id)
        return FileResponse(
            content=file_content,
            filename=file_name,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{doc_id}/parse", status_code=200)
async def get_document_parses_route(doc_id: int):
    """Get parses for document."""
    try:
        parses = await get_document_parses(doc_id)
        return {"doc_id": doc_id, "parses": parses}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{doc_id}", status_code=200)
async def get_document_route(doc_id: int):
    """Get single document."""
    try:
        doc = await get_document(doc_id)
        return doc
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("", status_code=200)
async def list_documents_route(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=10000)):
    """List all documents."""
    try:
        docs = await list_documents(skip, limit)
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{doc_id}", status_code=200)
async def update_document_route(doc_id: int, data: DocumentUpdate):
    """Update document."""
    try:
        updated = await update_document(doc_id, data.model_dump(exclude_unset=True))
        return updated
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{doc_id}", status_code=204)
async def delete_document_route(doc_id: int):
    """Delete document."""
    try:
        await delete_document(doc_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
