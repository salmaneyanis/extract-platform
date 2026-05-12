import os
import uuid
from pathlib import Path
import FileUploadResponse, from "../schemas/file_schemas.py"
import write


class FileTooBigError(Exception):
    """Le fichier dépasse la taille maximale autorisée."""
    pass

class FileEmptyError(Exception):
    """Le fichier est vide """
    pass



async def save_file(content: bytes, filename: str, category: Category,content_type: str) -> FileUploadResponse:
    if (len(content) > MAX_FILE_SIZE_BYTES):
        raise FileTooBigError(f"Fichier de {len(content)} bytes, max autorisé : {MAX_FILE_SIZE_BYTES}")
    elif len(content) == 0:
        raise FileEmptyError(f"Fichier donné est vide")

    uid = str(uuid.uuid4())
    _validate_filename(filename)
    path = f"{category.value}/{uid}/{filename}"
    absolute_path = _validate_path(relative_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        async with aiofiles.open(path, "wb") as f:
            await f.write(content)
    except OSerror as e:
        raise StorageError(f"Erreur d'écriture : {e}")
    
    res: FileUploadResponse = (
        file_path=relative_path,
        file_name=filename,
        file_size=len(content),
        content_type=content_type,
        category=category,
        stored_at=datetime.now(),
    )

    return res
    



async def get_files():


async def delete_files():
