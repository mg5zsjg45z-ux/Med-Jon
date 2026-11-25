"""API de teste. O cache e o transporte HTTP são locais ao processo."""
from contextlib import asynccontextmanager, ExitStack
from unittest.mock import AsyncMock, patch

import httpx
from app import store
from app.main import app


@asynccontextmanager
async def fixture(_):
    cache = {}
    seen = set()

    def provider(request):
        term = request.url.params.get("term")
        if term == "falha":
            return httpx.Response(503)
        if term in seen:
            raise AssertionError("Consulta repetida acionou o provedor")
        if term:
            seen.add(term)
            ids = [] if term == "vazio" else ["1234"]
            return httpx.Response(200, json={"esearchresult": {"idlist": ids}})
        return httpx.Response(200, json={"result": {"1234": {"title": "Estudo sintético",
            "articleids": [{"idtype": "doi", "value": "10.0000/teste"}]}}})

    def save(key, value, *_):
        cache[key] = value

    client = httpx.AsyncClient
    with ExitStack() as stack:
        stack.enter_context(patch.object(store, "lookup", AsyncMock(side_effect=cache.get)))
        stack.enter_context(patch.object(store, "save", AsyncMock(side_effect=save)))
        stack.enter_context(patch.object(store, "reserve", AsyncMock()))
        stack.enter_context(patch.object(httpx, "AsyncClient", side_effect=lambda **kw:
                                        client(transport=httpx.MockTransport(provider), **kw)))
        yield


app.router.lifespan_context = fixture
