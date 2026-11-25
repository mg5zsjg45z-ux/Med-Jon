import unittest
from app.services.firecrawl import scrape

class FirecrawlTests(unittest.IsolatedAsyncioTestCase):
    async def test_reject_unapproved_host(self):
        with self.assertRaises(ValueError):
            await scrape("https://example.com/")
    async def test_reject_query(self):
        with self.assertRaises(ValueError):
            await scrape("https://www.gov.br/?patient=example")
