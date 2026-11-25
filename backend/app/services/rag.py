import asyncio
import json
from app.services import storage, embeddings, research

def initialize():
    with storage.connect() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS literature_vectors (
            pmid text PRIMARY KEY, reference jsonb NOT NULL,
            embedding vector(768) NOT NULL, model text NOT NULL,
            retrieved_at timestamptz NOT NULL DEFAULT now())""")

def vector_literal(vector):
    return "[" + ",".join(str(float(x)) for x in vector) + "]"

def save(records, vectors):
    with storage.connect() as conn:
        for record, vector in zip(records, vectors, strict=True):
            conn.execute("""INSERT INTO literature_vectors(pmid,reference,embedding,model)
                VALUES (%s,%s::jsonb,%s::vector,%s)
                ON CONFLICT(pmid) DO UPDATE SET reference=excluded.reference,
                embedding=excluded.embedding, model=excluded.model, retrieved_at=now()""",
                (record["pmid"], json.dumps(record), vector_literal(vector), embeddings.MODEL))

def nearest(vector, limit):
    with storage.connect() as conn:
        rows = conn.execute("""SELECT reference, 1-(embedding <=> %s::vector) AS similarity, retrieved_at
            FROM literature_vectors WHERE model=%s
            ORDER BY embedding <=> %s::vector LIMIT %s""",
            (vector_literal(vector), embeddings.MODEL, vector_literal(vector), limit)).fetchall()
    return [{"reference": ref, "similarity": float(score), "retrieved_at": date.isoformat()} for ref, score, date in rows]

async def index(query, limit):
    records = [r for r in await research.literature(query, limit) if r.get("title")]
    if records:
        vectors = await embeddings.embed([r["title"] for r in records])
        await asyncio.to_thread(save, records, vectors)
    return records

async def retrieve(query, limit):
    vectors = await embeddings.embed([query])
    return await asyncio.to_thread(nearest, vectors[0], limit)

async def context(query, limit):
    hits = await retrieve(query, limit)
    return {"mode": "retrieval_only", "clinical_validation": False,
            "sources": hits, "context": [{"source_id": h["reference"]["pmid"],
            "text": h["reference"]["title"]} for h in hits],
            "limitations": "Somente títulos e metadados; não permite inferir recomendações clínicas."}
