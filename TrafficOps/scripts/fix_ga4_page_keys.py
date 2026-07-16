"""
scripts/fix_ga4_page_keys.py

One-time fix for data already synced before services/url_utils.py
was corrected. GA4 rows were stored keyed by bare path (e.g.
"/some-post") instead of full URL (e.g. "https://qajourney.net/some-post"),
so they never joined with GSC's pages. This clears ga4_sessions for
every site so the next GA4 sync (Backfill or Sync Recent, in the app)
rewrites them with the corrected key.

Does NOT touch gsc_queries or page_verdicts — those were never
affected by this bug.

Usage:
    python -m scripts.fix_ga4_page_keys
"""

from database.db import get_connection
from config.sites import SITES


def main():
    for site_id, config in SITES.items():
        if not config["db_path"].exists():
            print(f"{config['label']}: no database yet, skipping")
            continue

        conn = get_connection(config["db_path"])
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ga4_sessions")
        deleted = cursor.rowcount
        conn.commit()
        conn.close()

        print(f"{config['label']}: cleared {deleted} GA4 rows — re-sync GA4 to rebuild correctly")

    print("\nDone. Run Backfill (GA4) again in the app for each site you've already synced.")


if __name__ == "__main__":
    main()
