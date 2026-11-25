import unittest
from unittest.mock import patch, AsyncMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.routes import router
from app.services import abstracts, generation

class Phase5Tests(unittest.TestCase):
    def test_abstract(self):
        xml='<PubmedArticleSet><PubmedArticle><MedlineCitation><PMID>123</PMID><Article><Abstract><AbstractText Label="RESULTS">A <b>sample</b> result.</AbstractText></Abstract></Article></MedlineCitation></PubmedArticle></PubmedArticleSet>'
        self.assertEqual(abstracts.parse(xml),{"123":"RESULTS: A sample result."})
    def test_unknown_citation(self):
        with self.assertRaises(ValueError):
            generation.validate_output({"claims":[{"pmid":"999","quote":"This is a fabricated quote.","text":"Example"}]},{"123":"Real source"})
    def test_literal_quote(self):
        quote="This is an example source."
        self.assertEqual(len(generation.validate_output({"claims":[{"pmid":"123","quote":quote,"text":"Example"}]},{"123":quote})),1)
    def test_auth(self):
        app=FastAPI()
        app.include_router(router)
        with patch.dict("os.environ",{"MEDJON_API_KEY":"test-only"}):
            client=TestClient(app)
            self.assertEqual(client.post("/research/pubmed",json={"query":"asthma","bibliographic_only":True}).status_code,401)
            self.assertEqual(client.post("/research/pubmed",headers={"X-API-Key":"test-only"},json={"query":"asthma","bibliographic_only":False}).status_code,400)
    def test_mocked_endpoint(self):
        app=FastAPI()
        app.include_router(router)
        with patch.dict("os.environ",{"MEDJON_API_KEY":"test-only"}), patch("app.services.research.literature",new_callable=AsyncMock,return_value=[{"pmid":"123"}]):
            response=TestClient(app).post("/research/pubmed",headers={"X-API-Key":"test-only"},json={"query":"asthma","bibliographic_only":True})
            self.assertEqual(response.json(),[{"pmid":"123"}])
