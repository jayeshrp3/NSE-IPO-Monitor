import json
from urllib.parse import urlparse

import httpx


class OllamaUnavailable(Exception):
    pass


class OllamaTimeout(Exception):
    pass


class OllamaInvalidResponse(Exception):
    pass


class OllamaClient:
    def __init__(
        self,
        base_url: str = "http://127.0.0.1:11434",
        model: str = "llama3.2:3b",
        timeout: float = 120,
        transport: httpx.AsyncBaseTransport | None = None,
    ):
        parsed = urlparse(base_url)
        if parsed.scheme not in {"http", "https"} or parsed.hostname not in {
            "127.0.0.1",
            "localhost",
            "::1",
        }:
            raise ValueError("Ollama endpoint must use loopback")
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.transport = transport

    async def generate(self, messages: list[dict[str, str]]) -> str:
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                trust_env=False,
                transport=self.transport,
            ) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": False,
                        "format": "json",
                        "options": {"temperature": 0},
                    },
                )
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise OllamaTimeout("Local inference timed out.") from exc
        except httpx.HTTPError as exc:
            raise OllamaUnavailable("Local Ollama service is unavailable.") from exc
        try:
            payload = response.json()
        except ValueError as exc:
            raise OllamaInvalidResponse("Local model returned malformed JSON.") from exc
        message = payload.get("message")
        output = message.get("content") if isinstance(message, dict) else None
        if not isinstance(output, str):
            raise OllamaInvalidResponse("Local model returned an invalid response.")
        try:
            json.loads(output)
        except json.JSONDecodeError as exc:
            raise OllamaInvalidResponse("Local model returned malformed JSON.") from exc
        return output
