"""
main.py

FastAPI app entrypoint. Boots logging, initializes the database schema,
mounts routers. This is what gets run to start the backend.

Phase 1: headless only. Run with `uvicorn app.backend.main:app --reload`
and test via http://127.0.0.1:8317/docs — no UI exists yet.

Depends on: config.py, logging_setup.py, db/schema.py, routers/health.py
Called from: uvicorn (dev), later the pywebview launcher (Phase 4)
"""

import logging

from fastapi import FastAPI

from app.backend import config
from app.backend.logging_setup import configure_logging
from app.backend.db.schema import init_schema
from app.backend.chat.repository import mark_interrupted_on_startup
from app.backend.routers import health, chat

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="EAI Workstation", version="0.1.0")

app.include_router(health.router)
app.include_router(chat.router)


@app.on_event("startup")
def on_startup() -> None:
    """
    on_startup
    Runs once when the backend boots: ensures the database schema exists,
    then sweeps for any message left GENERATING from a previous session
    that crashed or lost power mid-generation, marking it INTERRUPTED.
    @return  None
    """
    logger.info("Starting EAI Workstation backend on %s:%d", config.HOST, config.PORT)
    init_schema()
    mark_interrupted_on_startup()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=config.HOST, port=config.PORT)
