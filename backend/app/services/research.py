import asyncio
from app.services import storage, pubmed, firecrawl

async def literature(query, limit=5):
    key = storage.key_for("pubmed", f"{limit}:{query}")
    cached = await asyncio.to_thread(storage.get_cached, key)
    if cached is not None:
        return cached
    records = await pubmed.search(query, limit)
    await asyncio.to_thread(storage.put_cached, key, records, 24)
    return records

async def guideline(url):
    key = storage.key_for("firecrawl", url)
    cached = await asyncio.to_thread(storage.get_cached, key)
    if cached is not None:
        return cached
    if not await asyncio.to_thread(storage.reserve_credits, 1):
        raise RuntimeError("Orçamento local indisponível")
    data = await firecrawl.scrape(url)
    await asyncio.to_thread(storage.put_cached, key, data)
    return data
