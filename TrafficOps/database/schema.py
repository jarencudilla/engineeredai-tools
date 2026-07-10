"""
database/schema.py

Defines the SQLite table structure for a single site's database.
Every site gets an identical schema — only the data differs.

Called once per site on first sync (CREATE TABLE IF NOT EXISTS is
idempotent, so this is safe to call on every startup too).
"""

CREATE_GSC_QUERIES_TABLE = """
CREATE TABLE IF NOT EXISTS gsc_queries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    page TEXT NOT NULL,
    clicks INTEGER NOT NULL,
    impressions INTEGER NOT NULL,
    ctr REAL NOT NULL,
    position REAL NOT NULL,
    date TEXT NOT NULL,
    synced_at TEXT NOT NULL DEFAULT (datetime('now')),
    -- A given query/page/date combination should only appear once per sync.
    -- Re-syncing the same date range overwrites rather than duplicates.
    UNIQUE(query, page, date)
);
"""

CREATE_GA4_SESSIONS_TABLE = """
CREATE TABLE IF NOT EXISTS ga4_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    page TEXT NOT NULL,
    sessions INTEGER NOT NULL,
    engaged_sessions INTEGER NOT NULL,
    bounce_rate REAL NOT NULL,
    avg_engagement_time_sec REAL NOT NULL,
    date TEXT NOT NULL,
    synced_at TEXT NOT NULL DEFAULT (datetime('now')),
    -- One row per page/date — re-syncing overwrites rather than duplicates.
    UNIQUE(page, date)
);
"""

# The judgment layer. This is the one table that isn't synced from
# an API — it's Jaren's own editorial calls, and it's the whole
# point of the app existing: GSC/GA4 will never store "rewrite this."
CREATE_PAGE_VERDICTS_TABLE = """
CREATE TABLE IF NOT EXISTS page_verdicts (
    page TEXT PRIMARY KEY,
    verdict TEXT NOT NULL,
    note TEXT,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""

# Indexes support the sort/filter operations the Queries and Pages
# modules need (Phase 2) without a full table scan on every interaction.
CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_gsc_queries_page ON gsc_queries(page);",
    "CREATE INDEX IF NOT EXISTS idx_gsc_queries_date ON gsc_queries(date);",
    "CREATE INDEX IF NOT EXISTS idx_gsc_queries_clicks ON gsc_queries(clicks DESC);",
    "CREATE INDEX IF NOT EXISTS idx_ga4_sessions_page ON ga4_sessions(page);",
    "CREATE INDEX IF NOT EXISTS idx_ga4_sessions_date ON ga4_sessions(date);",
]


def init_schema(conn):
    """
    Create all tables and indexes on the given connection if they
    don't already exist. Safe to call every time the app starts.

    @param conn  sqlite3.Connection  An open connection to a site's .db file
    """
    cursor = conn.cursor()
    cursor.execute(CREATE_GSC_QUERIES_TABLE)
    cursor.execute(CREATE_GA4_SESSIONS_TABLE)
    cursor.execute(CREATE_PAGE_VERDICTS_TABLE)
    for index_sql in CREATE_INDEXES:
        cursor.execute(index_sql)
    conn.commit()
