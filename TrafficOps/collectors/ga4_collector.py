"""
collectors/ga4_collector.py

Pulls raw GA4 landing-page performance for one site over a date range,
using the GA4 Data API (not Universal Analytics — that's shut down),
with pagination for large historical pulls.

This module ONLY collects — raw API response rows go straight to
services/ga4_normalizer.py for shaping. Same split as the GSC
collector, same reasoning: API response format changes stay isolated
to the normalizer.
"""

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange, Dimension, Metric, RunReportRequest
)

from collectors.google_auth import get_credentials

# GA4 Data API's max rows returned per request.
PAGE_SIZE = 100000


def fetch_ga4_landing_pages(site_config: dict, start_date: str, end_date: str) -> list:
    """
    Fetch ALL landing-page performance rows from the GA4 Data API for
    one site over a range, paginating past the per-request row cap.

    @param site_config  dict  One entry from config/sites.py
                               (needs ga4_property_id)
    @param start_date   str   ISO date, e.g. "2025-03-01"
    @param end_date     str   ISO date, e.g. "2026-07-01"
    @return list  Raw row objects as returned by the API — NOT normalized.
                   Concatenated across all pages.
    """
    property_id = site_config.get("ga4_property_id")
    if not property_id:
        raise ValueError(
            f"No ga4_property_id set for site '{site_config['label']}' "
            "in config/sites.py. Run scripts/discover_ga4_properties.py "
            "or find it in GA4 → Admin → Property Settings → Property ID."
        )

    creds = get_credentials()
    client = BetaAnalyticsDataClient(credentials=creds)

    all_rows = []
    offset = 0

    while True:
        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="landingPage"), Dimension(name="date")],
            metrics=[
                Metric(name="sessions"),
                Metric(name="engagedSessions"),
                Metric(name="bounceRate"),
                Metric(name="averageSessionDuration"),
            ],
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            limit=PAGE_SIZE,
            offset=offset,
        )

        response = client.run_report(request)
        all_rows.extend(response.rows)

        # NOTE: fewer rows than PAGE_SIZE means this was the last page.
        if len(response.rows) < PAGE_SIZE:
            break
        offset += PAGE_SIZE

    return all_rows
