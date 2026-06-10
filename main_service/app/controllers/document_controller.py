from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.schemas.document_schemas import ProcessResponse, Status
from app.services.orchestration_service import process_document

router = APIRouter(prefix="/documents", tags=["documents"])

@router.get("", status_code=200)
async def test():
    return {"test": "ok"}



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
