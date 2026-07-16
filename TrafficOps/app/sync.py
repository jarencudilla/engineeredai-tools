"""
app/sync.py

Orchestrates two distinct operations per data source — this is the
fix for the original design mistake, which only ever pulled a
rolling 7-day window and called it a sync. That never built a real
archive; it just kept re-fetching almost the same week.

BACKFILL: run once per site to pull full history (GSC: up to 16
months, the hard API limit; GA4: as far back as the property's data
goes) and store it permanently. This is what turns the local .db
into an actual archive instead of a mirror of GSC/GA4's own UI.

INCREMENTAL: run afterward, as often as you like, to append recent
days on top of the archive. Safe to re-run — INSERT OR REPLACE keyed
on (query, page, date) / (page, date) means overlapping days update
rather than duplicate.
"""

from datetime import date, timedelta

from collectors.gsc_collector import fetch_gsc_queries
from collectors.ga4_collector import fetch_ga4_landing_pages
from services.gsc_normalizer import normalize_gsc_rows
from services.ga4_normalizer import normalize_ga4_rows
from database.db import get_connection, save_gsc_rows, save_ga4_rows
from config.sites import get_site

# Hard cap enforced by the GSC API — see collectors/gsc_collector.py.
GSC_BACKFILL_MONTHS = 16

# GA4 retention varies by property; 16 months mirrors GSC's cap for
# a consistent archive window across both sources. Can be raised
# per-site later if a property's data goes back further.
GA4_BACKFILL_MONTHS = 16

# Default window for topping up the archive after the initial backfill.
INCREMENTAL_DAYS = 30


def backfill_site_gsc(site_id: str) -> dict:
    """
    One-time full-history pull for GSC. Run this once per site;
    after that, use sync_site_gsc_incremental to top up.

    @param site_id  str  Short site id, e.g. "qaj" (see config/sites.py)
    @return dict  Summary: {"site_id", "source", "rows_written", "start_date", "end_date"}
    """
    site_config = get_site(site_id)

    # NOTE: 3-day buffer stays clear of GSC's reporting lag.
    end_date = date.today() - timedelta(days=3)
    start_date = end_date - timedelta(days=GSC_BACKFILL_MONTHS * 30)

    raw_rows = fetch_gsc_queries(
        site_config,
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
    )
    normalized_rows = normalize_gsc_rows(raw_rows)

    conn = get_connection(site_config["db_path"])
    rows_written = save_gsc_rows(conn, normalized_rows)
    conn.close()

    return {
        "site_id": site_id,
        "source": "gsc-backfill",
        "rows_written": rows_written,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }


def sync_site_gsc_incremental(site_id: str, days_back: int = INCREMENTAL_DAYS) -> dict:
    """
    Top up the archive with recent days. Safe to run repeatedly —
    overlapping dates update existing rows rather than duplicate.

    @param site_id    str  Short site id, e.g. "qaj"
    @param days_back  int  How many recent days to pull (default 30)
    @return dict  Summary: {"site_id", "source", "rows_written", "start_date", "end_date"}
    """
    site_config = get_site(site_id)

    end_date = date.today() - timedelta(days=3)
    start_date = end_date - timedelta(days=days_back)

    raw_rows = fetch_gsc_queries(
        site_config,
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
    )
    normalized_rows = normalize_gsc_rows(raw_rows)

    conn = get_connection(site_config["db_path"])
    rows_written = save_gsc_rows(conn, normalized_rows)
    conn.close()

    return {
        "site_id": site_id,
        "source": "gsc-incremental",
        "rows_written": rows_written,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }


def backfill_site_ga4(site_id: str) -> dict:
    """
    One-time full-history pull for GA4. Run this once per site;
    after that, use sync_site_ga4_incremental to top up.

    @param site_id  str  Short site id, e.g. "qaj"
    @return dict  Summary: {"site_id", "source", "rows_written", "start_date", "end_date"}
    """
    site_config = get_site(site_id)

    end_date = date.today() - timedelta(days=1)
    start_date = end_date - timedelta(days=GA4_BACKFILL_MONTHS * 30)

    raw_rows = fetch_ga4_landing_pages(
        site_config,
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
    )
    normalized_rows = normalize_ga4_rows(raw_rows, site_domain=site_config["gsc_property"])

    conn = get_connection(site_config["db_path"])
    rows_written = save_ga4_rows(conn, normalized_rows)
    conn.close()

    return {
        "site_id": site_id,
        "source": "ga4-backfill",
        "rows_written": rows_written,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }


def sync_site_ga4_incremental(site_id: str, days_back: int = INCREMENTAL_DAYS) -> dict:
    """
    Top up the GA4 archive with recent days. Safe to run repeatedly.

    @param site_id    str  Short site id, e.g. "qaj"
    @param days_back  int  How many recent days to pull (default 30)
    @return dict  Summary: {"site_id", "source", "rows_written", "start_date", "end_date"}
    """
    site_config = get_site(site_id)

    end_date = date.today() - timedelta(days=1)
    start_date = end_date - timedelta(days=days_back)

    raw_rows = fetch_ga4_landing_pages(
        site_config,
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
    )
    normalized_rows = normalize_ga4_rows(raw_rows, site_domain=site_config["gsc_property"])

    conn = get_connection(site_config["db_path"])
    rows_written = save_ga4_rows(conn, normalized_rows)
    conn.close()

    return {
        "site_id": site_id,
        "source": "ga4-incremental",
        "rows_written": rows_written,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }
