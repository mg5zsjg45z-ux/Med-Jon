import os
import secrets
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from app.services import research, rag

def authorize(x_api_key: str = Header(default="")):
    expected = os.getenv("MEDJON_API_KEY", "")
    if not expected or not secrets.compare_digest(x_api_key, expected):
        raise HTTPException(401, "Acesso não autorizado")

router = APIRouter(prefix="/research", dependencies=[Depends(authorize)])

class Query(BaseModel):
    query: str = Field(min_length=2, max_length=500)
    limit: int = Field(default=5, ge=1, le=20)
    bibliographic_only: bool

def validate(body):
    if not body.bibliographic_only:
        raise HTTPException(400, "Somente consultas bibliográficas sem dados de pacientes")

@router.post("/pubmed")
async def pubmed(body: Query):
    validate(body)
    return await research.literature(body.query, body.limit)

@router.post("/index")
async def index(body: Query):
    validate(body)
    return await rag.index(body.query, body.limit)

@router.post("/semantic")
async def semantic(body: Query):
    validate(body)
    return await rag.retrieve(body.query, body.limit)

@router.post("/context")
async def context(body: Query):
    validate(body)
    return await rag.context(body.query, body.limit)
