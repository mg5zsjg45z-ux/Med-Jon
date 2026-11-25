"""Extração de páginas públicas previamente aprovadas; nunca envie dados clínicos."""
from datetime import datetime, timezone
import os
from app import store
from urllib.parse import urlsplit
import httpx

ALLOWED = {"www.gov.br", "www.who.int", "www.nice.org.uk"}

async def scrape(url: str) -> dict:
    parsed = urlsplit(url)
    if (parsed.scheme != "https" or parsed.netloc not in ALLOWED
            or parsed.query or parsed.fragment):
        raise ValueError("URL não aprovada")
    cache_id = store.cache_key("firecrawl", url)
    cached = await store.lookup(cache_id)
    if cached is not None:
        return cached
    key = os.environ.get("FIRECRAWL_API_KEY")
    if not key:
        raise RuntimeError("Configure FIRECRAWL_API_KEY localmente")
    async with httpx.AsyncClient(timeout=60) as client:
        await store.reserve("firecrawl")
        response = await client.post(
            "https://api.firecrawl.dev/v2/scrape",
            headers={"Authorization": f"Bearer {key}"},
            json={"url": url, "formats": ["markdown"], "onlyMainContent": True,
                  "parsers": [], "proxy": "basic"},
        )
        response.raise_for_status()
        result = response.json()
        if not result.get("success"):
            raise RuntimeError("Falha na extração")
        data = result["data"]
        if not isinstance(data.get("markdown"), str):
            raise ValueError("Resposta Firecrawl sem markdown")
        data["retrieved_at"] = datetime.now(timezone.utc).isoformat()
        await store.save(cache_id, data, "firecrawl", [{"url": url, "retrieved_at": data["retrieved_at"]}])
        return data
