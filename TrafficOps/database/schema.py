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

# Indexes support the sort/filter operations the Queries module needs
# (Phase 2) without a full table scan on every interaction.
CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_gsc_queries_page ON gsc_queries(page);",
    "CREATE INDEX IF NOT EXISTS idx_gsc_queries_date ON gsc_queries(date);",
    "CREATE INDEX IF NOT EXISTS idx_gsc_queries_clicks ON gsc_queries(clicks DESC);",
]


def init_schema(conn):
    """
    Create all tables and indexes on the given connection if they
    don't already exist. Safe to call every time the app starts.

    @param conn  sqlite3.Connection  An open connection to a site's .db file
    """
    cursor = conn.cursor()
    cursor.execute(CREATE_GSC_QUERIES_TABLE)
    for index_sql in CREATE_INDEXES:
        cursor.execute(index_sql)
    conn.commit()
