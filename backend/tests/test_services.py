import os
import unittest
from unittest.mock import AsyncMock, patch

import httpx
from app import store
from app.services import firecrawl, pubmed


class AdapterTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.lookup = self.enterContext(patch.object(store, "lookup", new_callable=AsyncMock))
        self.lookup.return_value = None
        self.reserve = self.enterContext(patch.object(store, "reserve", new_callable=AsyncMock))
        self.save = self.enterContext(patch.object(store, "save", new_callable=AsyncMock))
        self.requests = []
        self.responses = []

        def handler(request):
            self.requests.append(request)
            return self.responses.pop(0)

        client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        self.enterContext(patch.object(httpx, "AsyncClient", return_value=client))
        self.enterContext(patch.dict(os.environ, FIRECRAWL_API_KEY="teste"))

    async def test_pubmed_contract(self):
        self.responses = [
            httpx.Response(200, json={"esearchresult": {"idlist": ["123"]}}),
            httpx.Response(200, json={"result": {"123": {"title": "Sintético", "pubdate": "2025",
                "articleids": [{"idtype": "doi", "value": "10.0000/teste"}]}}}),
        ]
        articles = await pubmed.search("tema sintético", 100)
        first, second = self.requests
        self.assertTrue(first.url.path.endswith("/esearch.fcgi"))
        self.assertEqual(first.url.params["retmax"], "20")
        self.assertTrue(second.url.path.endswith("/esummary.fcgi"))
        self.assertEqual(second.url.params["id"], "123")
        self.assertNotIn("term", second.url.params)
        self.assertEqual(articles[0]["doi"], "10.0000/teste")
        self.assertIn("retrieved_at", articles[0])

    async def test_cached_empty_search(self):
        self.lookup.return_value = []
        self.assertEqual(await pubmed.search("tema"), [])
        self.reserve.assert_not_awaited()
        self.assertFalse(self.requests)

    async def test_firecrawl_contract(self):
        import json
        self.responses = [httpx.Response(200, json={"success": True, "data": {"markdown": "# Teste"}})]
        data = await firecrawl.scrape("https://www.who.int/")
        request, = self.requests
        self.assertEqual((request.method, str(request.url)), ("POST", "https://api.firecrawl.dev/v2/scrape"))
        self.assertEqual(request.headers["Authorization"], "Bearer teste")
        self.assertEqual(json.loads(request.content)["parsers"], [])
        self.assertEqual(data["markdown"], "# Teste")
        self.reserve.assert_awaited_once_with("firecrawl")
        self.save.assert_awaited_once()

    async def test_budget_blocks_http(self):
        self.reserve.side_effect = store.BudgetExceeded
        with self.assertRaises(store.BudgetExceeded):
            await firecrawl.scrape("https://www.who.int/")
        self.assertFalse(self.requests)

    async def test_provider_failure_is_not_cached(self):
        self.responses = [httpx.Response(429)]
        with self.assertRaises(httpx.HTTPStatusError):
            await firecrawl.scrape("https://www.who.int/")
        self.save.assert_not_awaited()
