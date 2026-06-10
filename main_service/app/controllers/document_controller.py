from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.schemas.document_schemas import ProcessResponse, Status, UploadResponse, ExtractOnlyResponse
from app.services.orchestration_service import process_document, upload_document, extract_and_save

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


@router.get("", status_code=200)
async def test():
    return {"test": "ok"}
