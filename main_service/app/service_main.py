from fastapi import FastAPI
from app.controllers.document_controller import router as document_router
from app.controllers.parses_controller import router as parses_router
from app.controllers.jobs_controller import router as jobs_router

app = FastAPI(title="Main Service")

app.include_router(document_router)
app.include_router(parses_router)
app.include_router(jobs_router)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "Main Service",
    }


@app.get("/")
async def root():
    return {"message": "Main Service is running"}