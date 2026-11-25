from typing import Annotated

import httpx
from psycopg import Error as DatabaseError
from pydantic import BaseModel, StringConstraints, Field
from fastapi import HTTPException
from app.services import pubmed
from app.store import RateLimited
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


class SearchRequest(BaseModel):
    query: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=300)]
    limit: int = Field(default=5, ge=1, le=20)


@app.post("/api/pubmed/search")
async def search_pubmed(request: SearchRequest):
    try:
        articles, cached = await pubmed.search_with_cache(request.query, request.limit)
    except RateLimited:
        raise HTTPException(429, "Aguarde um instante antes de pesquisar novamente.") from None
    except DatabaseError:
        raise HTTPException(503, "O banco de pesquisa está temporariamente indisponível.") from None
    except (httpx.HTTPError, RuntimeError, ValueError, KeyError, TypeError):
        raise HTTPException(502, "O PubMed está temporariamente indisponível.") from None
    return {"articles": articles, "cached": cached}
