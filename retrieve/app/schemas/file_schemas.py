from enum import Enum
from datetime import datetime
from app.config import MAX_FILE_SIZE_BYTES
from pydantic import BaseModel, field_validator



# classe python 
class Category(str,Enum):
    ORIGINALS = "originals"
    PARSES = "parses"
    ARTIFACTS = "artifacts"


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

    @field_validator("file_name")
    def verify_file_name(cls,name):
        """Vérifie le nom du fichier donné est valide """
        if not name:
            raise ValueError("Nom du fichier vide")
        return name

    @field_validator("file_size")
    @classmethod  
    def verify_file_size(cls,size):
        """Vérifie que la taille du fichié est valide """
        if size < 0 or size > MAX_FILE_SIZE_BYTES :
            raise ValueError("La taille du fichier est invalide, il doit être faire au maximum : {MAX_FILE_SIZE_BYTES}" )
        return size

    @field_validator("file_path")
    @classmethod  
    def verify_file_path(cls,path):
        """Vérifie que le chemin  du fichier est valide """
        if not path :
            raise ValueError("La taille du fichier est invalide, il doit être faire au maximum : {MAX_FILE_SIZE_BYTES}")
        return path

    @field_validator("file_type")
    @classmethod  
    def verify_file_type(cls,typefile):
        """Vérifie le type du fichier donné est valide """
        if not typefile:
            raise ValueError("type du fichier vide")
        return typefile 


#classe qui défini la structure de la réponse pour le deletefile qui sera renvoyé au service principale 
class FileDeleteResponse(BaseModel):
    file_name: str
    file_path: str
    deleted_at: datetime

    @field_validator("file_name")
    @classmethod 
    def verify_file_name(cls,name):
        """Vérifie le nom du fichier donné est valide """
        if not name or len(name) == 0:
            raise ValueError("Nom du fichier vide")
        return name
    
    @field_validator("file_path")
    @classmethod 
    def verify_file_path(cls,path):
        """Vérifie que le chemin  du fichier est valide """
        if not path or len(path) == 0:
            raise ValueError("La taille du fichier est invalide, il doit être faire au maximum :" + MAX_FILE_SIZE_BYTES)
        return path
