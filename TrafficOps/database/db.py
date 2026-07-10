"""
database/db.py

Handles opening a connection to a specific site's SQLite file and
writing/reading GSC and GA4 rows.

This is the ONLY module that touches sqlite3 directly. Collectors,
services, and UI all go through these functions — never open a
connection themselves. That keeps the "database only stores" rule
enforceable in one place.
"""

import sqlite3
from pathlib import Path

from database.schema import init_schema
from models.gsc_query import GSCQueryRow
from models.ga4_row import GA4Row


def get_connection(db_path: Path) -> sqlite3.Connection:
    """
    Open (and if needed, create) a site's database file.
    Ensures the parent directory and schema exist before returning.

    @param db_path  Path  Path to the site's .db file (from config/sites.py)
    @return sqlite3.Connection
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    init_schema(conn)
    return conn


def save_gsc_rows(conn: sqlite3.Connection, rows: list[GSCQueryRow]) -> int:
    """
    Insert normalized GSC rows into the database.
    Uses INSERT OR REPLACE keyed on (query, page, date) so re-running
    a sync for the same date range updates rather than duplicates.

    @param conn   sqlite3.Connection  Open connection to the target site's db
    @param rows   list[GSCQueryRow]   Normalized rows ready to store
    @return int   Number of rows written
    """
    cursor = conn.cursor()
    cursor.executemany(
        """
        INSERT OR REPLACE INTO gsc_queries
            (query, page, clicks, impressions, ctr, position, date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [(r.query, r.page, r.clicks, r.impressions, r.ctr, r.position, r.date) for r in rows],
    )
    conn.commit()
    return cursor.rowcount


def fetch_all_queries(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    """
    Return every stored GSC query row for this site, most recent
    date first, highest clicks first within a date.

    @param conn  sqlite3.Connection  Open connection to the site's db
    @return list[sqlite3.Row]
    """
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM gsc_queries ORDER BY date DESC, clicks DESC"
    )
    return cursor.fetchall()


def save_ga4_rows(conn: sqlite3.Connection, rows: list[GA4Row]) -> int:
    """
    Insert normalized GA4 rows into the database.
    Uses INSERT OR REPLACE keyed on (page, date) so re-running a sync
    for the same date range updates rather than duplicates.

    @param conn   sqlite3.Connection  Open connection to the target site's db
    @param rows   list[GA4Row]        Normalized rows ready to store
    @return int   Number of rows written
    """
    cursor = conn.cursor()
    cursor.executemany(
        """
        INSERT OR REPLACE INTO ga4_sessions
            (page, sessions, engaged_sessions, bounce_rate, avg_engagement_time_sec, date)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (r.page, r.sessions, r.engaged_sessions, r.bounce_rate, r.avg_engagement_time_sec, r.date)
            for r in rows
        ],
    )
    conn.commit()
    return cursor.rowcount


def fetch_all_sessions(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    """
    Return every stored GA4 session row for this site, most recent
    date first, highest sessions first within a date.

    @param conn  sqlite3.Connection  Open connection to the site's db
    @return list[sqlite3.Row]
    """
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM ga4_sessions ORDER BY date DESC, sessions DESC"
    )
    return cursor.fetchall()
