"""
routers/recall.py

Single endpoint: GET /search?q=... Global by default, spans every chat.

Depends on: recall/service.py
Called from: main.py (router registration)
"""

from fastapi import APIRouter

from app.backend.recall import service
from app.backend.recall.models import SearchResult

router = APIRouter()


@router.get("/search")
def search_messages(q: str, limit: int = 20) -> list[SearchResult]:
    """
    search_messages
    Full-text search across all chat history.
    @param   q      str  The search query.
    @param   limit  int  Max results, defaults to 20.
    @return  list[SearchResult]
    """
    return service.search(q, limit)
