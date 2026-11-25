"""Busca bibliográfica; não envie dados de pacientes."""
import asyncio
from datetime import datetime, timezone
import os
from app import store
import httpx

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

async def search(query: str, limit: int = 5) -> list[dict]:
    articles, _ = await search_with_cache(query, limit)
    return articles


async def search_with_cache(query: str, limit: int = 5) -> tuple[list[dict], bool]:
    params = {"db": "pubmed", "term": query, "retmode": "json",
              "retmax": max(1, min(limit, 20)), "tool": "medjon"}
    key = store.cache_key("pubmed", query, params["retmax"])
    cached = await store.lookup(key)
    if cached is not None:
        return cached, True
    for env, field in (("NCBI_API_KEY", "api_key"), ("NCBI_EMAIL", "email")):
        if os.getenv(env):
            params[field] = os.environ[env]
    async with httpx.AsyncClient(timeout=20) as client:
        await store.reserve("pubmed")
        response = await client.get(f"{BASE}/esearch.fcgi", params=params)
        if response.is_error:
            raise RuntimeError(f"Falha PubMed (HTTP {response.status_code})")
        ids = response.json()["esearchresult"]["idlist"]
        if not ids:
            await store.save(key, [], "pubmed", [])
            return [], False
        await asyncio.sleep(0.35)
        params.pop("term")
        params.pop("retmax")
        params["id"] = ",".join(ids)
        await store.reserve("pubmed")
        response = await client.get(f"{BASE}/esummary.fcgi", params=params)
        if response.is_error:
            raise RuntimeError(f"Falha PubMed (HTTP {response.status_code})")
        records = response.json()["result"]
        recovered = datetime.now(timezone.utc).isoformat()
        articles = [{"retrieved_at": recovered, "pmid": uid, "title": records[uid].get("title"),
                 "year_or_date": records[uid].get("pubdate"),
                 "doi": next((a["value"] for a in records[uid].get("articleids", [])
                              if a.get("idtype") == "doi"), None),
                 "url": f"https://pubmed.ncbi.nlm.nih.gov/{uid}/"}
                for uid in ids]
        await store.save(key, articles, "pubmed", articles)
        return articles, False
