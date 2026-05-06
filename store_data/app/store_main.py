from fastapi import FastAPI

app = FastAPI(title="Store Data Service")


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "Store Data Service",
    }


@app.get("/")
async def root():
    return {"message": " Store Data Service is running"}