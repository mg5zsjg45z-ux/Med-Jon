"""Busca bibliográfica; não envie dados de pacientes."""
import os
import httpx

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

async def search(query: str, limit: int = 5) -> list[dict]:
    params = {"db": "pubmed", "term": query, "retmode": "json",
              "retmax": max(1, min(limit, 20)), "tool": "medjon"}
    for env, field in (("NCBI_API_KEY", "api_key"), ("NCBI_EMAIL", "email")):
        if os.getenv(env):
            params[field] = os.environ[env]
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(f"{BASE}/esearch.fcgi", params=params)
        response.raise_for_status()
        ids = response.json()["esearchresult"]["idlist"]
        if not ids:
            return []
        params.pop("term")
        params.pop("retmax")
        params["id"] = ",".join(ids)
        response = await client.get(f"{BASE}/esummary.fcgi", params=params)
        response.raise_for_status()
        records = response.json()["result"]
        return [{"pmid": uid, "title": records[uid].get("title"),
                 "year_or_date": records[uid].get("pubdate"),
                 "authors": [a.get("name") for a in records[uid].get("authors", [])],
                 "journal": records[uid].get("fulljournalname"),
                 "doi": next((a["value"] for a in records[uid].get("articleids", [])
                              if a.get("idtype") == "doi"), None),
                 "url": f"https://pubmed.ncbi.nlm.nih.gov/{uid}/"}
                for uid in ids]
