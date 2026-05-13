from datetime import datetime
from pathlib import Path
from app.schemas.file_schemas import FileUploadResponse, FileDeleteResponse, Category
from fastapi.responses import StreamingResponse, FileResponse
import aiofiles
from app.config import DATA_DIR, MAX_FILE_SIZE_BYTES


class FileEmptyError(Exception):
    pass

class FileTooLargeError(Exception):
    pass

class InvalidPathError(Exception):
    pass

class StorageError(Exception):
    pass

class FileMissingError(Exception):
    pass



def _validate_filename(filename: str) -> None:
    """Valide qu'un nom de fichier est utilisable."""

    invalid_username_characters = ["/", "\\"]

    if not filename or not filename.strip() :
        raise InvalidPathError("Nom de fichier invalide")

    elif len(filename) > 255:
        raise InvalidPathError("Nom de fichier trop long")

    elif any(x in filename for x in invalid_username_characters):
        raise InvalidPathError("Nom de fichier invalide")
        
    elif filename in (".", ".."):
        raise InvalidPathError("Nom de fichier invalide")


def _validate_doc_id(doc_id: str) -> None:
    """Valide qu'un doc_id est utilisable comme nom de dossier """

    if not doc_id or not doc_id.strip():
        raise InvalidPathError("Le doc_id ne peut être vide")

    invalid_characters = ["/", "\\"]
    if any(c in doc_id for c in invalid_characters):
        raise InvalidPathError("Le doc_id contient des caractères interdits")

    if doc_id in (".",".."):
        raise InvalidPathError("doc_id invalide")
    


def _validate_path(file_path: str) -> Path:
    """
    Valide qu'un path est sûr et reste sous DATA_DIR.
    Retourne le path absolu validé.
    """
    

    if not file_path or not file_path.strip():
        raise InvalidPathError("Le chemin ne peut pas être vide")
    

    if file_path.startswith("/"):
        raise InvalidPathError("Le chemin doit être relatif, pas absolu")
    absolute_path = (DATA_DIR / file_path).resolve()


    try:
        absolute_path.relative_to(DATA_DIR.resolve())
    except ValueError:
        raise InvalidPathError(
            f"Le chemin sort de la zone autorisée : {file_path}"
        )
    
    return absolute_path


def _validate_size(content: bytes) -> None:
    """Valide que la taille du contenu est acceptable."""

    if len(content) == 0:
        raise FileEmptyError("Le fichier est vide")

    if len(content) > MAX_FILE_SIZE_BYTES:
        raise FileTooLargeError(
            f"Fichier trop volumineux : {len(content)} bytes "
            f"(maximum autorisé : {MAX_FILE_SIZE_BYTES} bytes)"
        )



async def save_file(content: bytes, filename: str, category: Category, content_type: str, doc_id: str) -> FileUploadResponse:
    """Sauvegarder un fichier dans un répertoire précis et retourner une réponse en cas de réussite."""
    _validate_filename(filename)
    _validate_size(content)
    _validate_doc_id(doc_id)

    path = f"{category.value}/{doc_id}/{filename}"
    absolute_path = _validate_path(path)
    absolute_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        async with aiofiles.open(absolute_path, "wb") as f:
            await f.write(content)
    except OSError as e:
        raise StorageError(f"Erreur d'écriture : {e}")

    res = FileUploadResponse(
        file_path=path,
        file_name=filename,
        file_size=len(content),
        content_type=content_type,
        category=category,
        stored_at=datetime.now(),
    )

    return res
    



async def get_file(file_path: str) -> Path:
    """Retourne le chemin absolu d'un fichier validé pour lecture."""
    
    absolute_path = _validate_path(file_path)
    
    if not absolute_path.is_file():
        raise FileMissingError(f"Fichier introuvable : {file_path}")
    
    return absolute_path



async def delete_file(file_path: str) -> FileDeleteResponse:
    absolute_path = _validate_path(file_path)
    
    if not absolute_path.is_file():
        raise FileMissingError(f"Fichier introuvable : {file_path}")

    try:
        absolute_path.unlink()
    except OSError as e:
        raise StorageError(f"Erreur de suppression :  {e}")
    
    res = FileDeleteResponse(
        file_name= absolute_path.name,
        file_path= file_path,
        deleted_at= datetime.now(),
    )
    return res

