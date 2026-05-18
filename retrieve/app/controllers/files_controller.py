from fastapi import APIRouter, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse

from app.schemas.file_schemas import (
    Category,
    FileUploadResponse,
    FileDeleteResponse,
)
from app.services.file_services import (
    save_file,
    get_file,
    delete_file,
    FileMissingError,
    FileTooLargeError,
    InvalidPathError,
    StorageError,
)


router = APIRouter(prefix="/files", tags=["files"])


@router.post("", status_code=201, response_model=FileUploadResponse)
async def upload(
    uploaded_file: UploadFile,
    category: Category = Form(...),
    doc_id: str = Form(...),
):
    """Upload un fichier sur le volume."""
    try:
        content = await uploaded_file.read()
        result = await save_file(
            content=content,
            filename=uploaded_file.filename,
            category=category,
            doc_id=doc_id,
        )
        return result
    except FileTooLargeError as e:
        raise HTTPException(status_code=413, detail=str(e))
    except InvalidPathError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except StorageError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{file_path:path}")
async def download(file_path: str):
    """Télécharge un fichier depuis le volume."""
    try:
        absolute_path = await get_file(file_path)
        return FileResponse(
            path=absolute_path,
            filename=absolute_path.name,
        )
    except FileMissingError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidPathError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except StorageError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{file_path:path}",
    status_code=200,
    response_model=FileDeleteResponse,
)
async def delete(file_path: str):
    """Supprime un fichier du volume."""
    try:
        result = await delete_file(file_path)
        return result
    except FileMissingError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidPathError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except StorageError as e:
        raise HTTPException(status_code=500, detail=str(e))