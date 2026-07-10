"""
services/ga4_normalizer.py

Converts a list of raw GA4 API row objects into GA4Row objects ready
for storage. Same role as services/gsc_normalizer.py — this is the
only file that needs to change if GA4's response shape changes.
"""

from services.url_utils import canonicalize_url
from models.ga4_row import GA4Row


def normalize_ga4_rows(raw_rows: list) -> list[GA4Row]:
    """
    Turn a list of raw GA4 API row objects into GA4Row instances,
    ready for database.db.save_ga4_rows().

    Rows were requested with dimensions [landingPage, date] and
    metrics [sessions, engagedSessions, bounceRate, averageSessionDuration]
    — order matters here because GA4 returns values positionally,
    not as named fields. See collectors/ga4_collector.py.

    @param raw_rows  list  Output of collectors.ga4_collector.fetch_ga4_landing_pages
                            (already a flat list — pagination handled
                            by the collector)
    @return list[GA4Row]
    """
    normalized = []

    for row in raw_rows:
        landing_page = row.dimension_values[0].value
        date_raw = row.dimension_values[1].value  # GA4 returns "YYYYMMDD"

        sessions = int(row.metric_values[0].value)
        engaged_sessions = int(row.metric_values[1].value)
        bounce_rate = float(row.metric_values[2].value)
        avg_engagement = float(row.metric_values[3].value)

        # NOTE: GA4 dates come back as "20260701" with no separators —
        # reformat to ISO so it matches GSC's date format for storage
        # and any future cross-source date filtering.
        iso_date = f"{date_raw[0:4]}-{date_raw[4:6]}-{date_raw[6:8]}"

        normalized.append(
            GA4Row(
                page=canonicalize_url(landing_page),
                sessions=sessions,
                engaged_sessions=engaged_sessions,
                bounce_rate=bounce_rate,
                avg_engagement_time_sec=avg_engagement,
                date=iso_date,
            )
        )

    return normalized
