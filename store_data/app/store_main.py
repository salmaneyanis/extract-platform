from fastapi import FastAPI
from app.controllers.document_controller import router as documents_router
from app.controllers.jobs_controller import router as jobs_router
from app.controllers.parses_controller import router as parses_router


app = FastAPI(title="Store Data Service")

app.include_router(documents_router)
app.include_router(jobs_router)
app.include_router(parses_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "store_data"}