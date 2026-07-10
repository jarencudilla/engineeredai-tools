"""
ollama/client.py

Thin HTTP wrapper around the Ollama API. Nothing else in the backend
should call Ollama's HTTP endpoints directly — they go through here,
so if the Ollama API ever changes, this is the only file that updates.

is_reachable/list_models are sync (used at startup and in the health
check). stream_chat is async, since generation runs as a background
asyncio task independent of any single request — see chat/generation_job.py.

Depends on: config.py, httpx
Called from: ollama/health.py, chat/generation_job.py
"""

import json

import httpx

from app.backend import config


def is_reachable() -> bool:
    """
    is_reachable
    Checks whether Ollama is running and responding at all.
    @return  bool  True if Ollama's API responds, False otherwise
                    (not installed, not running, or unreachable).
    """
    try:
        response = httpx.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=2.0)
        return response.status_code == 200
    except httpx.RequestError:
        return False


def list_models() -> list[str]:
    """
    list_models
    Returns the names of models currently pulled in Ollama.
    @return  list[str]  Model names, empty list if Ollama is unreachable.
    """
    try:
        response = httpx.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=2.0)
        response.raise_for_status()
        data = response.json()
        return [model["name"] for model in data.get("models", [])]
    except (httpx.RequestError, httpx.HTTPStatusError, KeyError):
        return []


async def stream_chat(messages: list[dict]):
    """
    stream_chat
    Async generator yielding response text chunks from Ollama's /api/chat
    endpoint as they arrive. Caller is responsible for accumulating them
    and deciding when to stop consuming (e.g. on a stop request).
    @param   messages  list[dict]  [{"role": "user"/"assistant", "content": str}, ...]
    @yield   str                   Each chunk of generated text as it arrives.
    """
    payload = {
        "model": config.DEFAULT_MODEL,
        "messages": messages,
        "stream": True,
    }

    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("POST", f"{config.OLLAMA_BASE_URL}/api/chat", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line:
                    continue
                chunk = json.loads(line)
                text = chunk.get("message", {}).get("content", "")
                if text:
                    yield text
                if chunk.get("done"):
                    break
