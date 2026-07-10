"""
services/gsc_normalizer.py

Converts raw GSC API rows into GSCQueryRow objects ready for storage.

This is where URL canonicalization lives. GSC can return the same
logical page with trailing-slash or protocol variations, which would
otherwise silently fragment one page's data into multiple rows.

If normalization rules need to change (e.g. a redirect rewrite changes
canonical URLs), this is the only file that needs to change.
"""

from urllib.parse import urlparse, urlunparse

from models.gsc_query import GSCQueryRow


def canonicalize_url(raw_url: str) -> str:
    """
    Normalize a URL so the same logical page always produces the
    same string, regardless of trailing slash or scheme quirks.

    @param raw_url  str  URL as returned by GSC
    @return str     Canonicalized URL
    """
    parsed = urlparse(raw_url)
    path = parsed.path.rstrip("/") or "/"
    # NOTE: query strings and fragments are dropped intentionally —
    # GSC already reports the page dimension without tracking params
    # in almost all cases, but this guards against edge cases.
    return urlunparse((parsed.scheme, parsed.netloc, path, "", "", ""))


def normalize_gsc_rows(raw_rows: list[dict], date: str) -> list[GSCQueryRow]:
    """
    Turn raw API rows into a list of GSCQueryRow, ready for
    database.save_gsc_rows().

    @param raw_rows  list[dict]  Output of collectors.gsc_collector.fetch_gsc_queries
    @param date      str         ISO date these rows represent (single sync = single date)
    @return list[GSCQueryRow]
    """
    normalized = []

    for row in raw_rows:
        query, page = row["keys"][0], row["keys"][1]

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
