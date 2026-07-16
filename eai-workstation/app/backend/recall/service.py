"""
recall/service.py

Thin wrapper around recall/repository.py. Currently a pass-through, but
this is where workspace-scoped filtering hooks in later (Phase 6), so
routers/recall.py doesn't need to change when that's added.

Depends on: recall/repository.py
Called from: routers/recall.py
"""

from app.backend.recall.models import SearchResult
from app.backend.recall import repository


def search(query: str, limit: int = 20) -> list[SearchResult]:
    """
    search
    Runs a global search across all chats. Pass-through for now.
    @param   query  str
    @param   limit  int
    @return  list[SearchResult]
    """
    return repository.search(query, limit)
