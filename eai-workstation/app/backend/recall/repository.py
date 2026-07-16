"""
recall/repository.py

The actual FTS5 search query. Spans every chat by default — global recall,
matching the global-chat-first decision, not scoped to a workspace unless
a caller explicitly asks for that later.

User input is sanitized before hitting FTS5's MATCH syntax: FTS5 treats
characters like quotes, hyphens, and asterisks as query operators, so raw
user text ("what's up - test?") could throw a syntax error or silently
mean something other than what the user typed. Each word gets wrapped as
a literal token instead, so search behaves like plain keyword matching
regardless of what punctuation the user includes.

Depends on: db/connection.py, recall/models.py
Called from: recall/service.py
"""

from app.backend.db.connection import get_connection
from app.backend.recall.models import SearchResult


def _sanitize_query(raw_query: str) -> str:
    """
    _sanitize_query
    Converts free-text user input into a safe FTS5 MATCH expression by
    wrapping each word as a literal quoted token, joined with AND. Turns
    "what's up - test" into '"what's" AND "up" AND "test"' rather than
    letting FTS5 interpret the hyphen as an operator.
    @param   raw_query  str
    @return  str         A string safe to pass to FTS5's MATCH.
    """
    words = raw_query.strip().split()
    if not words:
        return ""
    escaped = [f'"{word}"' for word in words]
    return " AND ".join(escaped)


def search(query: str, limit: int = 20) -> list[SearchResult]:
    """
    search
    Full-text search across every message, every chat, ranked by FTS5's
    default relevance (bm25). Returns an empty list for an empty query
    rather than erroring.
    @param   query  str
    @param   limit  int  Max results, defaults to 20.
    @return  list[SearchResult]
    """
    fts_query = _sanitize_query(query)
    if not fts_query:
        return []

    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT m.id, m.chat_id, m.role, m.content, m.status, m.created_at
            FROM messages_fts
            JOIN messages m ON m.id = messages_fts.rowid
            WHERE messages_fts MATCH ?
            ORDER BY rank
            LIMIT ?
            """,
            (fts_query, limit),
        ).fetchall()

        return [
            SearchResult(
                message_id=row["id"],
                chat_id=row["chat_id"],
                role=row["role"],
                content=row["content"],
                status=row["status"],
                created_at=row["created_at"],
            )
            for row in rows
        ]
    finally:
        conn.close()
