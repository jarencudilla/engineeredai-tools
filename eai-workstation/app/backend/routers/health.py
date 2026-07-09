"""
routers/health.py

Single endpoint: GET /health. Reports backend + Ollama status so we can
confirm the whole skeleton is wired correctly before building anything
on top of it — no UI needed, this is testable straight from /docs.

Depends on: ollama/health.py
Called from: main.py (router registration)
"""

from fastapi import APIRouter

from app.backend.ollama.health import check_ollama_status

router = APIRouter()


@router.get("/health")
def get_health() -> dict:
    """
    get_health
    Returns backend status plus Ollama reachability and model presence.
    @return  dict  {"backend": "ok", "ollama": {...}}
    """
    return {
        "backend": "ok",
        "ollama": check_ollama_status(),
    }
