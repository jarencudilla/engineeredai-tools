"""
services/url_utils.py

Shared URL canonicalization logic.

Used by BOTH the GSC and GA4 normalizers so that a page pulled from
either source produces the identical string. This matters most once
GSC and GA4 data need to be joined on page URL (e.g. "impressions
but no clicks" vs "clicks but no engagement" both need to match rows
by page). Duplicating this logic in two normalizers would risk them
drifting apart and breaking that join silently.
"""

from urllib.parse import urlparse, urlunparse


def canonicalize_url(raw_url: str) -> str:
    """
    Normalize a URL (or bare path) so the same logical page always
    produces the same string, regardless of trailing slash, scheme,
    or host quirks.

    @param raw_url  str  URL or path as returned by GSC or GA4
    @return str     Canonicalized URL or path
    """
    parsed = urlparse(raw_url)
    path = parsed.path.rstrip("/") or "/"
    # NOTE: query strings and fragments are dropped intentionally.
    # GA4's landingPage dimension can include tracking params;
    # GSC's page dimension almost never does. Dropping both keeps
    # the two sources joinable on the same key.
    return urlunparse((parsed.scheme, parsed.netloc, path, "", "", ""))
