"""
models/gsc_query.py

Data model for a single normalized GSC query row.

This is the shape everything downstream agrees on: the normalizer
produces these, the database module stores these, the UI reads these.
Nothing else in the app should invent its own dict shape for GSC data.
"""

from dataclasses import dataclass


@dataclass
class GSCQueryRow:
    """
    One row of Search Console query performance data,
    already normalized and ready to store.

    @param query        The search query string.
    @param page          The URL the query matched to.
    @param clicks        Total clicks for this query/page pair.
    @param impressions   Total impressions.
    @param ctr           Click-through rate as a float (0.0–1.0), not a percentage.
    @param position      Average position, as reported by GSC (float, 1-indexed).
    @param date           ISO date (YYYY-MM-DD) this row covers.
    """
    query: str
    page: str
    clicks: int
    impressions: int
    ctr: float
    position: float
    date: str
