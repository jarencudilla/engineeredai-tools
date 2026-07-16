"""
rotation_tracker.py

Tracks which rotation slot is next for each CAS page, in SQLite.
Single responsibility: read/advance rotation state. No generation logic here.
"""

import sqlite3
from pathlib import Path
from voice_profiles import PAGES

DB_PATH = Path(__file__).parent / "rotation.db"


def _init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS rotation_state (
            page_key TEXT PRIMARY KEY,
            last_index INTEGER NOT NULL DEFAULT -1
        )
        """
    )
    conn.commit()
    return conn


def get_next_slot(page_key: str) -> str:
    """
    Returns the next slot key for a page and advances its position.
    Cycles back to the start once it reaches the end of the slot list.
    """
    conn = _init_db()
    slot_keys = list(PAGES[page_key]["slots"].keys())

    row = conn.execute(
        "SELECT last_index FROM rotation_state WHERE page_key = ?", (page_key,)
    ).fetchone()

    last_index = row[0] if row else -1
    next_index = (last_index + 1) % len(slot_keys)

    conn.execute(
        """
        INSERT INTO rotation_state (page_key, last_index) VALUES (?, ?)
        ON CONFLICT(page_key) DO UPDATE SET last_index = excluded.last_index
        """,
        (page_key, next_index),
    )
    conn.commit()
    conn.close()

    return slot_keys[next_index]
