"""
chat/generation_job.py

A GenerationJob runs a single Ollama call as a background asyncio task,
completely independent of whatever HTTP request started it. This is the
piece that makes the four message end-states possible:

  - complete:     stream finished naturally
  - stopped:      user explicitly cancelled it (stop() called)
  - interrupted:  backend process died mid-generation (handled on next
                   startup by repository.mark_interrupted_on_startup)
  - error:        Ollama/model call failed

Why a background task instead of just streaming inside the request handler:
an HTTP client disconnecting (mobile losing signal, browser tab closed)
must NOT kill generation. The desktop backend keeps working regardless of
who's currently watching. The request handler becomes a subscriber to
this job, not the thing driving it.

Depends on: ollama/client.py, chat/repository.py, chat/models.py
Called from: chat/service.py
"""

import asyncio
import logging

from app.backend.ollama.client import stream_chat
from app.backend.chat import repository
from app.backend.chat.models import MessageStatus

logger = logging.getLogger(__name__)


class GenerationJob:
    """
    Runs one assistant response generation. Create with start(), consume
    output via subscribe(), cancel early via stop(). Always finalizes the
    message to SQLite exactly once, no matter how it ends.
    """

    def __init__(self, message_id: int, ollama_messages: list[dict]):
        self.message_id = message_id
        self._ollama_messages = ollama_messages
        self._accumulated = ""
        self._subscribers: list[asyncio.Queue] = []
        self._stop_requested = False
        self._task: asyncio.Task | None = None

    def start(self) -> None:
        """
        start
        Launches the generation as a background asyncio task. Returns
        immediately — the task keeps running even if nobody is subscribed.
        @return  None
        """
        self._task = asyncio.create_task(self._run())

    def subscribe(self) -> asyncio.Queue:
        """
        subscribe
        Registers a new listener for this job's output chunks. A client
        disconnecting just means it stops reading from its queue — it
        does not affect the job or any other subscriber.
        @return  asyncio.Queue  Chunks (str) arrive here, None signals end.
        """
        queue: asyncio.Queue = asyncio.Queue()
        self._subscribers.append(queue)
        return queue

    def stop(self) -> None:
        """
        stop
        Requests early cancellation. Checked between chunks in _run — the
        job finishes finalizing whatever was generated so far, marked STOPPED.
        @return  None
        """
        self._stop_requested = True

    async def _run(self) -> None:
        """
        _run
        The actual generation loop. Wrapped in try/finally so the message
        gets finalized to SQLite no matter how this ends: clean finish,
        explicit stop, or an exception from Ollama.
        @return  None
        """
        status = MessageStatus.COMPLETE
        try:
            async for chunk in stream_chat(self._ollama_messages):
                if self._stop_requested:
                    status = MessageStatus.STOPPED
                    break
                self._accumulated += chunk
                self._broadcast(chunk)
        except Exception:
            logger.exception("Generation failed for message %d", self.message_id)
            status = MessageStatus.ERROR
        finally:
            repository.finalize_message(self.message_id, self._accumulated, status)
            self._broadcast(None)  # signal end to all subscribers
            unregister(self.message_id)

    def _broadcast(self, chunk: str | None) -> None:
        """
        _broadcast
        Pushes a chunk (or None for end-of-stream) to every subscriber.
        @param   chunk  str | None
        @return  None
        """
        for queue in self._subscribers:
            queue.put_nowait(chunk)


# Registry of currently-running jobs, keyed by message_id, so a stop
# request (which only knows the message/chat, not the job object) can
# find the right job to cancel.
_active_jobs: dict[int, GenerationJob] = {}


def register(job: GenerationJob) -> None:
    """register — adds a job to the active registry."""
    _active_jobs[job.message_id] = job


def get(message_id: int) -> GenerationJob | None:
    """get — looks up a running job by message id, or None if not found/finished."""
    return _active_jobs.get(message_id)


def unregister(message_id: int) -> None:
    """unregister — removes a finished job from the registry."""
    _active_jobs.pop(message_id, None)
