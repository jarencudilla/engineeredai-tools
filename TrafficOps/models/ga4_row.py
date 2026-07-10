"""
models/ga4_row.py

Data model for a single normalized GA4 landing-page performance row.

Same role as models/gsc_query.py — the agreed shape between
normalizer, database, and UI. Nothing else should invent its own
dict shape for GA4 data.
"""

from dataclasses import dataclass


@dataclass
class GA4Row:
    """
    One row of GA4 landing-page performance for a single date.

    @param page              Landing page path (canonicalized).
    @param sessions          Total sessions.
    @param engaged_sessions  Sessions with meaningful engagement.
    @param bounce_rate       Float 0.0–1.0, not a percentage.
    @param avg_engagement_time_sec  Average engagement time in seconds.
    @param date              ISO date (YYYY-MM-DD) this row covers.
    """
    page: str
    sessions: int
    engaged_sessions: int
    bounce_rate: float
    avg_engagement_time_sec: float
    date: str
