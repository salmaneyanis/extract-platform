from fastapi import FastAPI

app = FastAPI(title="Main Service")


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "Main Service",
    }


@app.get("/")
async def root():
    return {"message": "Main Service is running"}