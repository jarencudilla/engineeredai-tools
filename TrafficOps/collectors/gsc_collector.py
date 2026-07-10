"""
collectors/gsc_collector.py

Pulls raw Search Console query data for one site over a date range.

This module ONLY collects — it returns whatever the API gives back,
untouched. Normalization (URL cleanup, type conversion, shaping into
GSCQueryRow) happens in services/gsc_normalizer.py, not here.

Keeping this separation means a change in Google's response format
only touches the normalizer, never this file.
"""

from googleapiclient.discovery import build

from collectors.gsc_auth import get_credentials

# GSC caps rows per request; pagination isn't implemented yet since
# the MVP slice (single site, recent date range) won't hit this limit.
# TODO: add pagination via startRow once real usage approaches 25k rows.
ROW_LIMIT = 25000


def fetch_gsc_queries(site_config: dict, start_date: str, end_date: str) -> list[dict]:
    """
    Fetch raw query/page performance rows from the GSC API for one site.

    @param site_config  dict  One entry from config/sites.py (needs
                               gsc_property and token_path)
    @param start_date   str   ISO date, e.g. "2026-06-01"
    @param end_date     str   ISO date, e.g. "2026-07-01"
    @return list[dict]  Raw rows as returned by the API — NOT normalized.
                         Each dict has keys: keys (list), clicks,
                         impressions, ctr, position.
    """
    creds = get_credentials(site_config["token_path"])
    service = build("searchconsole", "v1", credentials=creds)

    request_body = {
        "startDate": start_date,
        "endDate": end_date,
        # NOTE: dimensions order matters — normalizer expects
        # keys[0] = query, keys[1] = page, in that order.
        "dimensions": ["query", "page"],
        "rowLimit": ROW_LIMIT,
    }

    response = (
        service.searchanalytics()
        .query(siteUrl=site_config["gsc_property"], body=request_body)
        .execute()
    )

    return response.get("rows", [])
