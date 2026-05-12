from enum import Enum
from datetime import datetime

from pydantic import BaseModel, validator

MAX_FILE_SIZE_MB = int(os.getenv("RETRIEVE_MAX_FILE_SIZE_MB", "100"))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# classe python 
class Category(str,Enum):
    ORIGINALS = "originals"
    PARSES = "parses"
    ARTIFACTS = "artifacts"

#classe qui définie les status de requête
class Status(str,Enum):
    PENDING = "pending"
    DONE = "done"
    FAILED = "failed"

class FileExtension(str, Enum):
    PDF = ".pdf"
    PNG = ".png"
    JPG = ".jpg"
    JPEG = ".jpeg"
    DOCX = ".docx"
    HTML = ".html"


#classe qui défini la structure de la réponse pour l'uploadfile qui sera renvoyé au service principale 
class FileUploadResponse(BaseModel):
    file_name: str
    file_size: int
    file_path: str
    file_type: str
    category: Category
    stored_at: datetime
    status: Status

    @field_validator("file_name")
    def verify_file_name(cls,name):
        """Vérifie le nom du fichier donné est valide """
        if not name or len(name) = 0:
            raise ValueError("Nom du fichier vide")

    @field_validator("file_size")
    def verify_file_size(cls,size):
        """Vérifie que la taille du fichié est valide """
        if size < 0 or size > MAX_FILE_SIZE_BYTES :
            raise ValueError("La taille du fichier est invalide, il doit être faire au maximum :" + MAX_FILE_SIZE_BYTES)
    
    @field_validator("file_path")
    def verify_file_path(cls,file_path):
        """Vérifie que le chemin  du fichier est valide """
        if not file_path or len(file_path) = 0:
            raise ValueError("La taille du fichier est invalide, il doit être faire au maximum :" + MAX_FILE_SIZE_BYTES)
    
    @field_validator("filetype")
    def verify_file_type(cls,typefile):
        """Vérifie le type du fichier donné est valide """
        if not typefile or len(typefile) = 0:
            raise ValueError("type du fichier vide")


#classe qui défini la structure de la réponse pour le deletefile qui sera renvoyé au service principale 
class FileDeleteResponse(BaseModel):
    file_name: str
    file_path: str
    deleted_at: datetime
    status: Status

