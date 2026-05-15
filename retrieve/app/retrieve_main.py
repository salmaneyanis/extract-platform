# retrieve_main.py

from fastapi import FastAPI
from app.controllers.files_controller import router as files_router


app = FastAPI(title="Retrieve Service")


app.include_router(files_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "retrieve"}


@app.get("/")
async def root():
    return {"message": "Retrieve Service is running"}