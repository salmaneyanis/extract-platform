from fastapi import FastAPI
from app.controllers.document_controller import router as documents_router


app = FastAPI(title="Store Data Service")

app.include_router(documents_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "store_data"}