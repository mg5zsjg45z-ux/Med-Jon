import os
import math
import httpx

MODEL = "nomic-embed-text"
DIMENSIONS = 768

async def embed(texts: list[str]) -> list[list[float]]:
    if not texts or len(texts) > 20:
        raise ValueError("Lote inválido")
    base = os.getenv("OLLAMA_URL", "http://ollama:11434")
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(base + "/api/embed", json={"model": MODEL, "input": texts})
        response.raise_for_status()
        vectors = response.json()["embeddings"]
    if len(vectors) != len(texts) or any(len(v) != DIMENSIONS or not all(math.isfinite(x) for x in v) or not any(v) for v in vectors):
        raise ValueError("Embedding inválido")
    return vectors
