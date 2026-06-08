from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.schemas.extract_schemas import (
    ExtractResponse,
    ExtractProfile,
    Device,
    OutputFormat,
)
from app.services.pipeline_service import extract_document

router = APIRouter(prefix="/extract", tags=["extract"])


@router.post("", status_code=200, response_model=ExtractResponse)
async def extract(
    file: UploadFile = File(...),
    profile: str = Form(default="balanced"),
    device: str = Form(default="auto"),
    output_format: str = Form(default="markdown"),
):
    """Extract document to markdown/json."""
    try:
        profile_enum = ExtractProfile(profile.lower())
        device_enum = Device(device.lower())
        output_format_enum = OutputFormat(output_format.lower())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid enum value: {e}")

    try:
        file_content = await file.read()
        result = extract_document(
            file_content=file_content,
            profile=profile_enum,
            output_format=output_format_enum,
            device=device_enum,
        )

        if result["status"] == "failed":
            raise HTTPException(status_code=400, detail=result["metadata"].get("error"))

        return ExtractResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
