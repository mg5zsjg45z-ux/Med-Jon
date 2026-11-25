from fastapi import FastAPI

from contextlib import asynccontextmanager
from app.store import initialize


@asynccontextmanager
async def lifespan(app):
    await initialize()
    yield


app = FastAPI(title="Med-Jon", version="0.2.0", lifespan=lifespan)

@app.get("/health")
def health():
    return {"status": "ok", "clinical_validation": False}
