from fastapi import FastAPI, File, UploadFile
from app.schemas.file_schemas import Category
from app.services.file_services import save_file, FileEmptyError, FileTooLargeError, InvalidPathError, StorageError

app = FastAPI(title="Retrieve Service")


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "Retrieve Service",
    }


@app.get("/")
async def root():
    return {"message": " Retrieve Service is running"}

@app.post("/files")
async def upload(file: UploadFile, category: Category):
    pass

