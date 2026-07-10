"""
app/sync.py

Orchestrates the MVP sync loop for a single site:
fetch (collector) -> normalize (service) -> store (database).

This is the only place that wires those three layers together.
UI code calls sync_site(), it never talks to collectors or the
database directly.
"""

from datetime import date, timedelta

from collectors.gsc_collector import fetch_gsc_queries
from services.gsc_normalizer import normalize_gsc_rows
from database.db import get_connection, save_gsc_rows
from config.sites import get_site


def sync_site(site_id: str, days_back: int = 7) -> dict:
    """
    Run a full GSC sync for one site and store the results.

    @param site_id    str  Short site id, e.g. "qaj" (see config/sites.py)
    @param days_back  int  How many days of history to pull (default 7).
                            GSC data has a ~2-3 day reporting lag, so
                            "today" is intentionally excluded.
    @return dict  Summary: {"site_id", "rows_written", "start_date", "end_date"}
    """
    site_config = get_site(site_id)

    # NOTE: end_date is 3 days back to stay clear of GSC's reporting
    # lag — pulling the last 1-2 days usually returns incomplete data.
    end_date = date.today() - timedelta(days=3)
    start_date = end_date - timedelta(days=days_back)

    raw_rows = fetch_gsc_queries(
        site_config,
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
    )

    # NOTE: MVP treats the whole range as one batch dated at end_date.
    # Day-by-day granularity can be added later by looping per date
    # instead of pulling the range in one call.
    normalized_rows = normalize_gsc_rows(raw_rows, date=end_date.isoformat())

    conn = get_connection(site_config["db_path"])
    rows_written = save_gsc_rows(conn, normalized_rows)
    conn.close()

    return {
        "site_id": site_id,
        "rows_written": rows_written,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }
