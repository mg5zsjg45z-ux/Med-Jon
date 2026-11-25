import asyncio
import os
import unittest
from unittest.mock import patch

from app import store


@unittest.skipUnless(os.getenv("PGDATABASE") == "medjon_test", "requer banco dedicado medjon_test")
class DatabaseTests(unittest.IsolatedAsyncioTestCase):
    async def test_storage_and_limits(self):
        await store.initialize()
        async with store.connection() as conn:
            await conn.execute("TRUNCATE monthly_usage, provider_rate, research_cache, sources")
            cursor = await conn.execute("SELECT '[1,0]'::vector <-> '[0,1]'::vector")
            self.assertAlmostEqual((await cursor.fetchone())[0], 2**0.5)
        with patch.dict(os.environ, FIRECRAWL_MONTHLY_LIMIT="1"):
            outcomes = await asyncio.gather(*(store.reserve("firecrawl") for _ in range(2)),
                                            return_exceptions=True)
            self.assertEqual(outcomes.count(None), 1)
            self.assertTrue(any(isinstance(item, store.RateLimited) for item in outcomes))
            await asyncio.sleep(0.36)
            with self.assertRaises(store.BudgetExceeded):
                await store.reserve("firecrawl")
        source = {"url": "https://example.org/", "retrieved_at": "2026-01-01T00:00:00Z"}
        await store.save("teste", [source], "teste", [source])
        self.assertEqual(await store.lookup("teste"), [source])
        async with store.connection() as conn:
            cursor = await conn.execute("SELECT url FROM sources")
            self.assertEqual((await cursor.fetchone())[0], source["url"])
            await conn.execute("UPDATE research_cache SET expires_at=now()")
        self.assertIsNone(await store.lookup("teste"))
