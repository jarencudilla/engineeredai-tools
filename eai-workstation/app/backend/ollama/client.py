"""
ollama/client.py

Thin HTTP wrapper around the Ollama API. Nothing else in the backend
should call Ollama's HTTP endpoints directly — they go through here,
so if the Ollama API ever changes, this is the only file that updates.

Depends on: config.py, httpx
Called from: ollama/health.py, and the future chat endpoint (Phase 2)
"""

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
