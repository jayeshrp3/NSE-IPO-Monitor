import asyncio

import httpx
import pytest

from app.services.ollama_client import (
    OllamaClient,
    OllamaInvalidResponse,
    OllamaTimeout,
    OllamaUnavailable,
)


def test_non_loopback_endpoint_is_rejected():
    with pytest.raises(ValueError):
        OllamaClient(base_url="https://example.com", model="model")


def test_unavailable_local_service_has_explicit_error():
    client = OllamaClient(
        base_url="http://127.0.0.1:1",
        model="test",
        timeout=0.1,
    )

    async def run():
        with pytest.raises((OllamaUnavailable, OllamaTimeout)):
            await client.generate([{"role": "user", "content": "test"}])

    asyncio.run(run())


def test_malformed_local_model_response_is_explicitly_rejected():
    async def handler(request):
        assert request.url.host == "127.0.0.1"
        assert request.url.path == "/api/chat"
        return httpx.Response(200, json={"message": {"content": "{not-json"}})

    client = OllamaClient(
        base_url="http://127.0.0.1:11434",
        model="test",
        transport=httpx.MockTransport(handler),
    )

    async def run():
        with pytest.raises(OllamaInvalidResponse):
            await client.generate([{"role": "user", "content": "test"}])

    asyncio.run(run())
