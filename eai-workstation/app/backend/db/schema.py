"""
db/schema.py

Defines the database schema and runs it on startup. Tracks a schema_version
so future phases can add migrations instead of guessing what's already there.

Phase 1 only creates schema_version — chat/message tables land in Phase 2.

Depends on: db/connection.py
Called from: main.py (on startup)
"""

import logging

from app.backend.db.connection import get_connection

logger = logging.getLogger(__name__)

# Bump this and add a migration step whenever the schema changes.
CURRENT_SCHEMA_VERSION = 1


def init_schema() -> None:
    """
    init_schema
    Creates the schema_version table if it doesn't exist and records
    the current version. Safe to call on every startup — it's a no-op
    if the schema is already at the current version.
    @return  None
    """
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER NOT NULL
            )
            """
        )

        existing = conn.execute("SELECT version FROM schema_version").fetchone()

        if existing is None:
            conn.execute(
                "INSERT INTO schema_version (version) VALUES (?)",
                (CURRENT_SCHEMA_VERSION,),
            )
            conn.commit()
            logger.info("Initialized schema at version %d", CURRENT_SCHEMA_VERSION)
        else:
            logger.info("Schema already at version %d", existing["version"])
    finally:
        conn.close()
