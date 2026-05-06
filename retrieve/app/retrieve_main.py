from fastapi import FastAPI

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