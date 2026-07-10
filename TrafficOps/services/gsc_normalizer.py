"""
services/gsc_normalizer.py

Converts raw GSC API rows into GSCQueryRow objects ready for storage.

URL canonicalization is handled by services/url_utils.py, shared with
the GA4 normalizer so both sources key pages identically.
"""

from services.url_utils import canonicalize_url
from models.gsc_query import GSCQueryRow


def normalize_gsc_rows(raw_rows: list[dict]) -> list[GSCQueryRow]:
    """
    Turn raw API rows into a list of GSCQueryRow, ready for
    database.save_gsc_rows().

    Each row carries its own date (collectors.gsc_collector requests
    "date" as a dimension), so a multi-month backfill produces one
    row per query/page/day, not one row per query/page for the whole
    range — that granularity is what makes decay/comparison analysis
    possible later.

    @param raw_rows  list[dict]  Output of collectors.gsc_collector.fetch_gsc_queries
    @return list[GSCQueryRow]
    """
    normalized = []

    for row in raw_rows:
        date, query, page = row["keys"][0], row["keys"][1], row["keys"][2]

        normalized.append(
            GSCQueryRow(
                query=query,
                page=canonicalize_url(page),
                clicks=int(row.get("clicks", 0)),
                impressions=int(row.get("impressions", 0)),
                ctr=float(row.get("ctr", 0.0)),
                position=float(row.get("position", 0.0)),
                date=date,
            )
        )

    return normalized
