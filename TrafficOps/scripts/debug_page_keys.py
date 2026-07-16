"""
scripts/debug_page_keys.py

Diagnostic only — no changes made. Prints a sample of page keys as
actually stored in gsc_queries vs ga4_sessions for one site, plus
how many pages overlap between the two. If the join is broken, this
shows exactly what the two sides look like instead of guessing.

Usage:
    python -m scripts.debug_page_keys hobbyengineered
    (use the site_id from config/sites.py, e.g. qaj, eai, he, etc.)
"""

import sys

from database.db import get_connection
from config.sites import get_site


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.debug_page_keys <site_id>")
        print("e.g.:  python -m scripts.debug_page_keys he")
        return

    site_id = sys.argv[1]
    site_config = get_site(site_id)
    conn = get_connection(site_config["db_path"])
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT page FROM gsc_queries LIMIT 10")
    gsc_pages = [row["page"] for row in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT page FROM ga4_sessions LIMIT 10")
    ga4_pages = [row["page"] for row in cursor.fetchall()]

    cursor.execute("SELECT COUNT(DISTINCT page) FROM gsc_queries")
    gsc_total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT page) FROM ga4_sessions")
    ga4_total = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*) FROM (
            SELECT DISTINCT g.page FROM gsc_queries g
            INNER JOIN ga4_sessions a ON a.page = g.page
        )
        """
    )
    overlap = cursor.fetchone()[0]

    conn.close()

    print(f"Site: {site_config['label']}\n")
    print(f"Sample GSC page keys ({gsc_total} distinct total):")
    for p in gsc_pages:
        print(f"  {p!r}")

    print(f"\nSample GA4 page keys ({ga4_total} distinct total):")
    for p in ga4_pages:
        print(f"  {p!r}")

    print(f"\nPages present in BOTH sources (exact string match): {overlap}")

    if overlap == 0 and gsc_total > 0 and ga4_total > 0:
        print(
            "\n⚠ Zero overlap despite both having data — the keys are "
            "still mismatched. Compare the sample keys above by eye: "
            "check scheme (http vs https), trailing slash, or domain "
            "differences between the two lists."
        )


if __name__ == "__main__":
    main()
