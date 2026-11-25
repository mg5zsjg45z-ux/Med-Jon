import unittest
from unittest.mock import AsyncMock, patch
from app.services import rag

class RagTests(unittest.IsolatedAsyncioTestCase):
    async def test_empty_index(self):
        with patch.object(rag.research, "literature", new_callable=AsyncMock, return_value=[]), patch.object(rag.embeddings, "embed", new_callable=AsyncMock) as embed:
            self.assertEqual(await rag.index("asthma", 5), [])
            embed.assert_not_awaited()

    async def test_context_preserves_pmid(self):
        hit = {"reference": {"pmid": "123", "title": "Example"}, "similarity": 0.8}
        with patch.object(rag, "retrieve", new_callable=AsyncMock, return_value=[hit]):
            result = await rag.context("asthma", 5)
            self.assertEqual(result["context"][0]["source_id"], "123")
            self.assertFalse(result["clinical_validation"])
