"""
chat/repository.py

All SQLite reads/writes for chats and messages. Nothing in this file knows
about Ollama, streaming, or job lifecycles — it only knows SQL. That
separation is what lets generation_job.py and service.py reuse these
functions without duplicating queries.

Depends on: db/connection.py, chat/models.py
Called from: chat/generation_job.py, chat/service.py, routers/chat.py
"""

import logging

from app.backend.db.connection import get_connection
from app.backend.chat.models import MessageStatus

logger = logging.getLogger(__name__)


def create_chat(title: str = "New Chat") -> int:
    """
    create_chat
    Inserts a new chat row.
    @param   title  str  Chat title, defaults to "New Chat".
    @return  int         The new chat's id.
    """
    conn = get_connection()
    try:
        cursor = conn.execute("INSERT INTO chats (title) VALUES (?)", (title,))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def save_user_message(chat_id: int, content: str) -> int:
    """
    save_user_message
    Saves the user's side of an exchange immediately, before any call to
    Ollama — so even if generation never starts, the user's message isn't lost.
    @param   chat_id  int
    @param   content  str
    @return  int       The new message's id.
    """
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO messages (chat_id, role, content, status) VALUES (?, 'user', ?, 'complete')",
            (chat_id, content),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def create_pending_assistant_message(chat_id: int) -> int:
    """
    create_pending_assistant_message
    Creates the assistant's message row up front, with status GENERATING
    and empty content, before Ollama produces anything. This row gets
    updated in place as generation proceeds and finalized when it ends.
    @param   chat_id  int
    @return  int       The new message's id.
    """
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO messages (chat_id, role, content, status) VALUES (?, 'assistant', '', 'generating')",
            (chat_id,),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def finalize_message(message_id: int, content: str, status: MessageStatus) -> None:
    """
    finalize_message
    Writes the final accumulated content and end status for a message.
    Called exactly once per message, whether it completed, was stopped,
    errored, or the process died (in which case this runs on the next
    startup instead — see mark_interrupted_on_startup).
    @param   message_id  int
    @param   content     str
    @param   status      MessageStatus
    @return  None
    """
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE messages SET content = ?, status = ? WHERE id = ?",
            (content, status.value, message_id),
        )
        conn.commit()
    finally:
        conn.close()


def get_messages(chat_id: int) -> list[dict]:
    """
    get_messages
    Returns all messages for a chat, oldest first.
    @param   chat_id  int
    @return  list[dict]
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM messages WHERE chat_id = ? ORDER BY id ASC",
            (chat_id,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def mark_interrupted_on_startup() -> int:
    """
    mark_interrupted_on_startup
    Runs once when the backend boots. Any message still in GENERATING
    status means the previous process died mid-generation (power loss,
    force quit) without ever reaching finalize_message. Mark those
    INTERRUPTED so recall never confuses them with a real answer.
    @return  int  Number of messages marked interrupted.
    """
    conn = get_connection()
    try:
        cursor = conn.execute(
            "UPDATE messages SET status = 'interrupted' WHERE status = 'generating'"
        )
        conn.commit()
        count = cursor.rowcount
        if count > 0:
            logger.warning("Marked %d message(s) as interrupted from a previous session", count)
        return count
    finally:
        conn.close()
