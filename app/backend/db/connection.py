"""
db/connection.py

Owns the SQLite connection. Every part of the backend that needs the
database goes through get_connection() rather than opening its own
connection — keeps pragmas (like foreign keys, FTS5) consistent everywhere.

Depends on: config.py
Called from: db/schema.py, and any future router/service that reads/writes data.
"""

import sqlite3

from app.backend import config


def get_connection() -> sqlite3.Connection:
    """
    get_connection
    Opens a SQLite connection to the app database, creating the data
    directory first if this is the very first run.
    @return  sqlite3.Connection
    """
    config.ensure_data_dir()

    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row  # lets callers access columns by name

    # Foreign keys are off by default in SQLite — turn them on so
    # future tables (Phase 2+) with relationships actually enforce them.
    conn.execute("PRAGMA foreign_keys = ON")

    return conn
