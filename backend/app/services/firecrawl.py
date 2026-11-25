"""Extração de páginas públicas previamente aprovadas; nunca envie dados clínicos."""
import os
from urllib.parse import urlsplit
import httpx

ALLOWED = {"www.gov.br", "www.who.int", "www.nice.org.uk"}

async def scrape(url: str) -> dict:
    parsed = urlsplit(url)
    if (parsed.scheme != "https" or parsed.netloc not in ALLOWED
            or parsed.query or parsed.fragment):
        raise ValueError("URL não aprovada")
    key = os.environ.get("FIRECRAWL_API_KEY")
    if not key:
        raise RuntimeError("Configure FIRECRAWL_API_KEY localmente")
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            "https://api.firecrawl.dev/v2/scrape",
            headers={"Authorization": f"Bearer {key}"},
            json={"url": url, "formats": ["markdown"], "onlyMainContent": True},
        )
        response.raise_for_status()
        result = response.json()
        if not result.get("success"):
            raise RuntimeError("Falha na extração")
        return result["data"]
