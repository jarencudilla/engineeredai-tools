"""
recall/models.py

Response schema for search results.

Depends on: nothing.
Called from: recall/repository.py, routers/recall.py
"""

from pydantic import BaseModel


class SearchResult(BaseModel):
    """A single matched message, with enough context to jump back to it."""
    message_id: int
    chat_id: int
    role: str
    content: str
    status: str
    created_at: str
