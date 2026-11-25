from contextlib import asynccontextmanager
import asyncio
from fastapi import FastAPI
from app.services import storage, rag
from app.routes import router

@asynccontextmanager
async def lifespan(app):
    await asyncio.to_thread(storage.initialize)
    await asyncio.to_thread(rag.initialize)
    yield

app = FastAPI(title="Med-Jon", version="0.1.0-alpha", lifespan=lifespan)

@app.get("/health")
def health():
    return {"status": "ok", "clinical_validation": False}

app.include_router(router)
