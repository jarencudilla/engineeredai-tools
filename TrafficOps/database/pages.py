"""
database/pages.py

Page-level data access: rolling up query/session data by page, and
CRUD for the verdict judgment layer (page_verdicts table).

Split out from database/db.py because that file handles raw
GSC/GA4 row storage — this file is specifically about the page-level
view, which is a different concern even though both touch sqlite3.
"""

import sqlite3


def fetch_page_rollup(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    """
    Return one row per page, aggregating all stored GSC and GA4 data
    for that page across every synced date. This is the data behind
    the Pages tab — the view built for making a rewrite/delete/leave-it
    call, not for scanning individual query rows.

    LEFT JOINs mean a page shows up even if only one source has data
    for it (e.g. GA4 tracked a session on a page GSC hasn't indexed yet).

    @param conn  sqlite3.Connection  Open connection to the site's db
    @return list[sqlite3.Row]  Columns: page, total_impressions,
            total_clicks, avg_ctr, avg_position, total_sessions,
            total_engaged_sessions, verdict
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        WITH gsc_agg AS (
            SELECT
                page,
                SUM(impressions) AS total_impressions,
                SUM(clicks) AS total_clicks,
                AVG(ctr) AS avg_ctr,
                AVG(position) AS avg_position
            FROM gsc_queries
            GROUP BY page
        ),
        ga4_agg AS (
            SELECT
                page,
                SUM(sessions) AS total_sessions,
                SUM(engaged_sessions) AS total_engaged_sessions
            FROM ga4_sessions
            GROUP BY page
        )
        SELECT
            all_pages.page AS page,
            COALESCE(gsc_agg.total_impressions, 0) AS total_impressions,
            COALESCE(gsc_agg.total_clicks, 0) AS total_clicks,
            COALESCE(gsc_agg.avg_ctr, 0) AS avg_ctr,
            COALESCE(gsc_agg.avg_position, 0) AS avg_position,
            COALESCE(ga4_agg.total_sessions, 0) AS total_sessions,
            COALESCE(ga4_agg.total_engaged_sessions, 0) AS total_engaged_sessions,
            v.verdict AS verdict
        FROM
            (SELECT DISTINCT page FROM gsc_queries
             UNION
             SELECT DISTINCT page FROM ga4_sessions) AS all_pages
        -- NOTE: joining against pre-aggregated subqueries (not the raw
        -- tables) is deliberate — joining two one-to-many tables
        -- directly on page would fan out (every GSC row x every GA4
        -- row per page) and silently inflate both sums.
        LEFT JOIN gsc_agg ON gsc_agg.page = all_pages.page
        LEFT JOIN ga4_agg ON ga4_agg.page = all_pages.page
        LEFT JOIN page_verdicts v ON v.page = all_pages.page
        ORDER BY total_impressions DESC
        """
    )
    return cursor.fetchall()


def fetch_queries_for_page(conn: sqlite3.Connection, page: str) -> list[sqlite3.Row]:
    """
    Return every GSC query row for a single page, most recent first.
    Feeds the Inspector's "queries driving this page" view.

    @param conn  sqlite3.Connection  Open connection to the site's db
    @param page  str  Canonicalized page URL (matches gsc_queries.page)
    @return list[sqlite3.Row]
    """
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM gsc_queries WHERE page = ? ORDER BY date DESC, clicks DESC",
        (page,),
    )
    return cursor.fetchall()


def fetch_sessions_for_page(conn: sqlite3.Connection, page: str) -> list[sqlite3.Row]:
    """
    Return every GA4 session row for a single page, most recent first.
    Feeds the Inspector's GA4 trend view.

    @param conn  sqlite3.Connection  Open connection to the site's db
    @param page  str  Canonicalized page URL (matches ga4_sessions.page)
    @return list[sqlite3.Row]
    """
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM ga4_sessions WHERE page = ? ORDER BY date DESC",
        (page,),
    )
    return cursor.fetchall()


def set_verdict(conn: sqlite3.Connection, page: str, verdict: str, note: str = "") -> None:
    """
    Set (or overwrite) the editorial verdict for a page. This is the
    judgment layer — the one thing in the whole app that isn't synced
    from an API, it's Jaren's own call.

    @param conn     sqlite3.Connection  Open connection to the site's db
    @param page     str  Canonicalized page URL
    @param verdict  str  One of: "rewrite", "delete", "leave_it", "new_post_needed"
    @param note     str  Optional free-text note alongside the verdict
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO page_verdicts (page, verdict, note, updated_at)
        VALUES (?, ?, ?, datetime('now'))
        ON CONFLICT(page) DO UPDATE SET
            verdict = excluded.verdict,
            note = excluded.note,
            updated_at = excluded.updated_at
        """,
        (page, verdict, note),
    )
    conn.commit()


def get_verdict(conn: sqlite3.Connection, page: str) -> sqlite3.Row | None:
    """
    Fetch the current verdict for a page, if one has been set.

    @param conn  sqlite3.Connection  Open connection to the site's db
    @param page  str  Canonicalized page URL
    @return sqlite3.Row | None
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM page_verdicts WHERE page = ?", (page,))
    return cursor.fetchone()
