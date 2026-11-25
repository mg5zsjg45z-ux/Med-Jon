import os
import xml.etree.ElementTree as ET
import httpx

def parse(xml):
    if "<!ENTITY" in xml.upper():
        raise ValueError("XML não permitido")
    root = ET.fromstring(xml)
    result = {}
    for article in root.findall(".//PubmedArticle"):
        pmid = article.findtext("./MedlineCitation/PMID")
        sections = []
        for node in article.findall("./MedlineCitation/Article/Abstract/AbstractText"):
            text = "".join(node.itertext()).strip()
            if text:
                sections.append((node.get("Label", "") + ": " if node.get("Label") else "") + text)
        if pmid and sections:
            result[pmid] = "\n".join(sections)
    return result

async def fetch(ids):
    if not ids:
        return {}
    if len(ids) > 20 or any(not x.isascii() or not x.isdigit() for x in ids):
        raise ValueError("PMID inválido")
    params = {"db":"pubmed","id":",".join(ids),"retmode":"xml","tool":"medjon"}
    for env, field in (("NCBI_API_KEY","api_key"),("NCBI_EMAIL","email")):
        if os.getenv(env):
            params[field] = os.environ[env]
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",params=params)
        response.raise_for_status()
        if len(response.content) > 8_000_000:
            raise ValueError("Resposta extensa")
        return parse(response.text)
