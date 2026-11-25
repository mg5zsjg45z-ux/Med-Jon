"""Persistência compartilhada entre processos. Os relógios de controle são do banco."""
import hashlib
import json
import os
from contextlib import asynccontextmanager
from pathlib import Path

import psycopg
from psycopg.types.json import Jsonb


class BudgetExceeded(RuntimeError):
    pass


class RateLimited(RuntimeError):
    pass


@asynccontextmanager
async def connection():
    async with await psycopg.AsyncConnection.connect(connect_timeout=5) as conn:
        yield conn


async def initialize():
    async with connection() as conn:
        await conn.execute("SELECT pg_advisory_xact_lock(1296385098)")
        await conn.execute(Path(__file__).with_name("schema.sql").read_text())


def cache_key(provider, *parts):
    return hashlib.sha256(json.dumps([provider, *parts]).encode()).hexdigest()


async def lookup(key):
    async with connection() as conn:
        cursor = await conn.execute(
            "SELECT payload FROM research_cache WHERE cache_key=%s AND expires_at > now()", (key,)
        )
        row = await cursor.fetchone()
        return None if row is None else row[0]


async def save(key, payload, provider, sources):
    async with connection() as conn:
        for source in sorted(sources, key=lambda record: record["url"]):
            await conn.execute(
                """INSERT INTO sources(provider,url,pmid,doi,retrieved_at) VALUES (%s,%s,%s,%s,%s)
                   ON CONFLICT (provider,url) DO UPDATE SET retrieved_at=excluded.retrieved_at,
                   pmid=excluded.pmid, doi=excluded.doi
                   WHERE sources.retrieved_at <= excluded.retrieved_at""",
                (provider, source["url"], source.get("pmid"), source.get("doi"), source["retrieved_at"]),
            )
        await conn.execute(
            """INSERT INTO research_cache VALUES (%s,%s,now()+interval '24 hours')
               ON CONFLICT (cache_key) DO UPDATE SET payload=excluded.payload, expires_at=excluded.expires_at""",
            (key, Jsonb(payload)),
        )


async def reserve(provider):
    async with connection() as conn:
        cursor = await conn.execute(
            """INSERT INTO provider_rate VALUES (%s,clock_timestamp()+interval '350 milliseconds')
               ON CONFLICT (provider) DO UPDATE SET next_request=clock_timestamp()+interval '350 milliseconds'
               WHERE provider_rate.next_request <= clock_timestamp() RETURNING provider""", (provider,)
        )
        if not await cursor.fetchone():
            raise RateLimited("Limite de frequência atingido")
        if provider == "firecrawl":
            limit = int(os.getenv("FIRECRAWL_MONTHLY_LIMIT", "800"))
            cursor = await conn.execute(
                """INSERT INTO monthly_usage SELECT date_trunc('month', now() AT TIME ZONE 'UTC')::date,1
                   WHERE %s > 0 ON CONFLICT (month) DO UPDATE SET reserved=monthly_usage.reserved+1
                   WHERE monthly_usage.reserved < %s RETURNING reserved""", (limit, limit)
            )
            if not await cursor.fetchone():
                raise BudgetExceeded("Orçamento mensal esgotado")
