import unittest
from unittest.mock import patch, AsyncMock
from app.services import research

class ResearchTests(unittest.IsolatedAsyncioTestCase):
    async def test_cache_hit(self):
        with patch.object(research.storage, "get_cached", return_value=[]) as cache, patch.object(research.pubmed, "search", new_callable=AsyncMock) as search:
            self.assertEqual(await research.literature("hypertension"), [])
            cache.assert_called_once()
            search.assert_not_awaited()

    async def test_budget_denial(self):
        with patch.object(research.storage, "get_cached", return_value=None), patch.object(research.storage, "reserve_credits", return_value=False), patch.object(research.firecrawl, "scrape", new_callable=AsyncMock) as scrape:
            with self.assertRaises(RuntimeError):
                await research.guideline("https://www.who.int/")
            scrape.assert_not_awaited()
