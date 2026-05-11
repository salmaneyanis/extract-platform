from fastapi import FastAPI,File, UploadFile

from file_schemas.py import Category
import pydantic

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
    str filename = file.filename

