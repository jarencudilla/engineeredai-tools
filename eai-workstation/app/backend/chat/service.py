"""
chat/service.py

Orchestrates a chat exchange: save the user message immediately, create
a pending assistant message, start a GenerationJob for it. This is the
only file that decides the *order* things happen in — repository only
knows SQL, generation_job only knows how to run one generation.

Depends on: chat/repository.py, chat/generation_job.py
Called from: routers/chat.py
"""

from app.backend.chat import repository
from app.backend.chat.generation_job import GenerationJob, register, get


def start_generation(chat_id: int, user_content: str) -> int:
    """
    start_generation
    Saves the user's message, creates a pending assistant message, and
    launches generation for it in the background. Returns immediately —
    the caller subscribes to the returned message_id to stream output.
    @param   chat_id       int
    @param   user_content  str
    @return  int            The assistant message's id (subscribe to this).
    """
    repository.save_user_message(chat_id, user_content)

    history = repository.get_messages(chat_id)
    ollama_messages = [
        {"role": m["role"], "content": m["content"]}
        for m in history
        if m["status"] != "generating"  # exclude the pending row we're about to create
    ]

    message_id = repository.create_pending_assistant_message(chat_id)

    job = GenerationJob(message_id, ollama_messages)
    register(job)
    job.start()

    return message_id


def stop_generation(message_id: int) -> bool:
    """
    stop_generation
    Requests early cancellation of a running job. No-op if the job
    already finished or was never running (e.g. stale message id).
    @param   message_id  int
    @return  bool         True if a running job was found and stopped.
    """
    job = get(message_id)
    if job is None:
        return False
    job.stop()
    return True
