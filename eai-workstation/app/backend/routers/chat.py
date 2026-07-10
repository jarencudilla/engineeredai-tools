"""
routers/chat.py

Chat endpoints. The streaming endpoint is a thin subscriber to a
GenerationJob, not the thing driving generation — see generation_job.py
for why that separation exists (client disconnects must not kill
generation running for the desktop).

Depends on: chat/service.py, chat/repository.py, chat/generation_job.py
Called from: main.py (router registration)
"""

import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.backend.chat import service, repository
from app.backend.chat.generation_job import get as get_job
from app.backend.chat.models import SendMessageRequest

router = APIRouter()


@router.post("/chats")
def create_chat() -> dict:
    """
    create_chat
    Creates a new empty chat.
    @return  dict  {"chat_id": int}
    """
    chat_id = repository.create_chat()
    return {"chat_id": chat_id}


@router.get("/chats/{chat_id}/messages")
def list_messages(chat_id: int) -> list[dict]:
    """
    list_messages
    Returns all messages for a chat, oldest first.
    @param   chat_id  int
    @return  list[dict]
    """
    return repository.get_messages(chat_id)


@router.post("/chats/{chat_id}/messages")
async def send_message(chat_id: int, body: SendMessageRequest):
    """
    send_message
    Saves the user's message, starts generation, and streams the
    assistant's response back as it's produced. Subscribes to the job
    immediately after starting it, before any await, so no chunks are
    missed between job creation and subscription.
    @param   chat_id  int
    @param   body     SendMessageRequest
    @return  StreamingResponse  newline-delimited JSON chunks
    """
    message_id = service.start_generation(chat_id, body.content)

    job = get_job(message_id)
    if job is None:
        # Job already finished (e.g. instant error) before we could subscribe.
        raise HTTPException(status_code=500, detail="Generation ended before it could be streamed")

    queue = job.subscribe()

    async def event_stream():
        yield json.dumps({"message_id": message_id}) + "\n"
        while True:
            chunk = await queue.get()
            if chunk is None:
                break
            yield json.dumps({"chunk": chunk}) + "\n"

    return StreamingResponse(event_stream(), media_type="application/x-ndjson")


@router.post("/messages/{message_id}/stop")
def stop_message(message_id: int) -> dict:
    """
    stop_message
    Requests early cancellation of a running generation. The message
    will be finalized with status STOPPED, not silently discarded.
    @param   message_id  int
    @return  dict         {"stopped": bool}
    """
    stopped = service.stop_generation(message_id)
    return {"stopped": stopped}
