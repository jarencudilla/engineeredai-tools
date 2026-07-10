"""
chat/models.py

Request/response schemas for the chat endpoints, plus the MessageStatus
enum that tracks how a generation actually ended.

Depends on: nothing (base module for the chat package).
Called from: chat/repository.py, chat/generation_job.py, routers/chat.py
"""

from enum import Enum

from pydantic import BaseModel


class MessageStatus(str, Enum):
    """
    Tracks how an assistant message's generation ended. Distinguishing
    these matters: a message a user deliberately stopped should never be
    mistaken for a complete answer later during recall.
    """
    GENERATING = "generating"    # still in progress
    COMPLETE = "complete"        # finished naturally
    STOPPED = "stopped"          # user explicitly cancelled it
    INTERRUPTED = "interrupted"  # backend died mid-generation (power loss, crash)
    ERROR = "error"              # Ollama/model call failed


class SendMessageRequest(BaseModel):
    """Body for POST /chats/{chat_id}/messages"""
    content: str


class ChatSummary(BaseModel):
    """A chat as listed, no message content."""
    id: int
    title: str
    created_at: str


class MessageOut(BaseModel):
    """A single message as returned to a client."""
    id: int
    chat_id: int
    role: str
    content: str
    status: MessageStatus
    created_at: str
