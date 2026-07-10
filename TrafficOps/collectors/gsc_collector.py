"""
collectors/gsc_collector.py

Pulls raw Search Console query data for one site over a date range,
with per-day granularity and pagination for large pulls.

This module ONLY collects — it returns whatever the API gives back,
untouched. Normalization (URL cleanup, type conversion, shaping into
GSCQueryRow) happens in services/gsc_normalizer.py, not here.
"""

from googleapiclient.discovery import build

from collectors.google_auth import get_credentials

# Hard cap enforced by the GSC API itself, not a choice made here.
ROW_LIMIT = 25000


def fetch_gsc_queries(site_config: dict, start_date: str, end_date: str) -> list[dict]:
    """
    Fetch ALL query/page/date rows from the GSC API for one site over
    a range, paginating past the 25,000-row-per-request cap as needed.

    NOTE: "date" is included as a dimension so every row carries its
    own date, rather than the caller batching a whole range under one
    date. This is what makes a real historical archive possible —
    without per-row dates, backfilling 16 months would collapse into
    one meaningless "totals" row per query/page.

    @param site_config  dict  One entry from config/sites.py (needs gsc_property)
    @param start_date   str   ISO date, e.g. "2025-03-01"
    @param end_date     str   ISO date, e.g. "2026-07-01"
    @return list[dict]  Raw rows as returned by the API — NOT normalized.
                         Each dict has keys: keys (list: [date, query, page]),
                         clicks, impressions, ctr, position.
    """
    creds = get_credentials()
    service = build("searchconsole", "v1", credentials=creds)

    all_rows = []
    start_row = 0

    while True:
        request_body = {
            "startDate": start_date,
            "endDate": end_date,
            # NOTE: dimensions order matters — normalizer expects
            # keys[0] = date, keys[1] = query, keys[2] = page.
            "dimensions": ["date", "query", "page"],
            "rowLimit": ROW_LIMIT,
            "startRow": start_row,
        }

        response = (
            service.searchanalytics()
            .query(siteUrl=site_config["gsc_property"], body=request_body)
            .execute()
        )

        page_rows = response.get("rows", [])
        all_rows.extend(page_rows)

        # NOTE: fewer rows than ROW_LIMIT means this was the last page.
        if len(page_rows) < ROW_LIMIT:
            break
        start_row += ROW_LIMIT

    return all_rows
