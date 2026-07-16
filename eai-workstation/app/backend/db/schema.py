"""
db/schema.py

Defines the database schema and runs it on startup. Tracks a schema_version
so future phases can add migrations instead of guessing what's already there.

Version 2 (Phase 2): adds chats + messages tables. Messages carry a status
column (generating / complete / stopped / interrupted / error) because a
generation's lifecycle is independent of any single HTTP request — see
chat/generation_job.py for why that separation exists.

Version 3 (Phase 3): adds an FTS5 virtual table mirroring messages.content,
kept in sync via triggers (not app code) so recall/repository.py never has
to remember to update the search index — every insert and update to
messages is automatically reflected. A message starts as an empty string
(status=generating) and gets its real content on finalize; the AFTER UPDATE
trigger handles that transition the same way it handles any other edit.

Depends on: db/connection.py
Called from: main.py (on startup)
"""

import logging

from app.backend.db.connection import get_connection

logger = logging.getLogger(__name__)

# Bump this and add a migration step whenever the schema changes.
CURRENT_SCHEMA_VERSION = 3


def init_schema() -> None:
    """
    init_schema
    Creates schema tables if they don't exist and records the current
    version. Safe to call on every startup.
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

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL DEFAULT 'New Chat',
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                content TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'complete'
                    CHECK(status IN ('generating', 'complete', 'stopped', 'interrupted', 'error')),
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (chat_id) REFERENCES chats(id)
            )
            """
        )

        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_messages_chat_id ON messages(chat_id)"
        )

        _init_fts(conn)
        _set_version(conn)
    finally:
        conn.close()


def _init_fts(conn) -> None:
    """
    _init_fts
    Creates the FTS5 virtual table (external content, backed by messages.id
    as rowid) and the triggers that keep it synced automatically. No app
    code writes to messages_fts directly — these triggers are the only sync
    mechanism, by design, so chat/repository.py never needed to change.
    @param   conn  sqlite3.Connection
    @return  None
    """
    conn.execute(
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(
            content,
            content='messages',
            content_rowid='id'
        )
        """
    )

    conn.execute(
        """
        CREATE TRIGGER IF NOT EXISTS messages_ai AFTER INSERT ON messages BEGIN
            INSERT INTO messages_fts(rowid, content) VALUES (new.id, new.content);
        END
        """
    )

    conn.execute(
        """
        CREATE TRIGGER IF NOT EXISTS messages_ad AFTER DELETE ON messages BEGIN
            INSERT INTO messages_fts(messages_fts, rowid, content) VALUES('delete', old.id, old.content);
        END
        """
    )

    conn.execute(
        """
        CREATE TRIGGER IF NOT EXISTS messages_au AFTER UPDATE ON messages BEGIN
            INSERT INTO messages_fts(messages_fts, rowid, content) VALUES('delete', old.id, old.content);
            INSERT INTO messages_fts(rowid, content) VALUES (new.id, new.content);
        END
        """
    )


def _set_version(conn) -> None:
    """
    _set_version
    Records the current schema version if not already present.
    @param   conn  sqlite3.Connection
    @return  None
    """
    existing = conn.execute("SELECT version FROM schema_version").fetchone()

    if existing is None:
        conn.execute(
            "INSERT INTO schema_version (version) VALUES (?)",
            (CURRENT_SCHEMA_VERSION,),
        )
        conn.commit()
        logger.info("Initialized schema at version %d", CURRENT_SCHEMA_VERSION)
    elif existing["version"] < CURRENT_SCHEMA_VERSION:
        conn.execute("UPDATE schema_version SET version = ?", (CURRENT_SCHEMA_VERSION,))
        conn.commit()
        logger.info(
            "Migrated schema from version %d to %d", existing["version"], CURRENT_SCHEMA_VERSION
        )
    else:
        conn.commit()
        logger.info("Schema already at version %d", existing["version"])
