"""
services/url_utils.py

Shared URL canonicalization logic.

Used by BOTH the GSC and GA4 normalizers so that a page pulled from
either source produces the identical string. This matters most once
GSC and GA4 data need to be joined on page URL — and it's the exact
join that was silently broken: GA4's landingPage dimension returns a
BARE PATH ("/some-post"), not a full URL, while GSC's page dimension
always returns the full URL ("https://site.com/some-post"). Without
knowing the site's own domain, those two never canonicalize to the
same string, and GSC/GA4 rows for the same page fail to join.
"""

from urllib.parse import urlparse, urlunparse


def canonicalize_url(raw_url: str, base_url: str = None) -> str:
    """
    Normalize a URL (or bare path) so the same logical page always
    produces the same string, regardless of trailing slash, scheme,
    or host quirks — and regardless of whether the source gave a full
    URL (GSC) or a bare path (GA4's landingPage).

    @param raw_url  str  URL or path as returned by GSC or GA4
    @param base_url str  The site's own domain (e.g. "https://qajourney.net/"),
                          used to fill in scheme+host when raw_url has
                          neither. Required for GA4 input; not needed
                          for GSC input, which already includes both.
    @return str     Canonicalized URL, always with scheme+host+path
    """
    parsed = urlparse(raw_url)

    if parsed.netloc:
        scheme, netloc = parsed.scheme, parsed.netloc
    elif base_url:
        base_parsed = urlparse(base_url)
        scheme, netloc = base_parsed.scheme, base_parsed.netloc
    else:
        # NOTE: no host on raw_url and no base_url given — this will
        # produce a host-less key that won't match anything. Callers
        # normalizing GA4 data must always pass base_url.
        scheme, netloc = parsed.scheme, parsed.netloc

    path = parsed.path.rstrip("/") or "/"
    # NOTE: query strings and fragments are dropped intentionally.
    # GA4's landingPage dimension can include tracking params;
    # GSC's page dimension almost never does. Dropping both keeps
    # the two sources joinable on the same key.
    return urlunparse((scheme, netloc, path, "", "", ""))
