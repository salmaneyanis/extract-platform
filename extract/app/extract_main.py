from fastapi import FastAPI

app = FastAPI(title="Extract Service")


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "Extract Service",
    }


@app.get("/")
async def root():
    return {"message": "Extract Service is running"}