from fastapi import FastAPI
from app.controllers.extract_controller import router as extract_router

app = FastAPI(title="Extract Service")

app.include_router(extract_router)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "Extract Service",
    }


@app.get("/")
async def root():
    return {"message": "Extract Service is running"}