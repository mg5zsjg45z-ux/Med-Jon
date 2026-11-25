from contextlib import asynccontextmanager
import asyncio
from fastapi import FastAPI
from app.services import storage

@asynccontextmanager
async def lifespan(app):
    await asyncio.to_thread(storage.initialize)
    yield

app = FastAPI(title="Med-Jon", version="0.2.0", lifespan=lifespan)

@app.get("/health")
def health():
    return {"status": "ok", "clinical_validation": False}
