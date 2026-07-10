"""
scripts/discover_ga4_properties.py

Run this ONCE. It finds every GA4 property the trafficops-reader
service account can see, matches each one to a site in config/sites.py
by comparing domains (GA4's web stream URL vs each site's gsc_property),
and writes the matched ga4_property_id values directly into
config/sites.py. No manual copy-paste, no six lookups.

Usage:
    python -m scripts.discover_ga4_properties

Sites that don't get a confident domain match are left untouched and
reported at the end, so you're never guessing which number silently
went where.
"""

import re
from urllib.parse import urlparse

from google.analytics.admin import AnalyticsAdminServiceClient
from google.analytics.admin_v1beta.types import (
    ListPropertiesRequest, ListDataStreamsRequest
)

from collectors.google_auth import get_credentials
from config.sites import SITES, BASE_DIR

SITES_FILE = BASE_DIR / "config" / "sites.py"


def _domain(url: str) -> str:
    """Strip protocol/www/trailing slash so domains compare cleanly."""
    host = urlparse(url).netloc or urlparse(url).path
    return host.lower().removeprefix("www.").rstrip("/")


def _discover_properties(client) -> dict:
    """
    @return dict  {domain: property_id} for every GA4 web property
                  the service account can see.
    """
    domain_to_property_id = {}

    for account in client.list_accounts():
        prop_request = ListPropertiesRequest(filter=f"parent:{account.name}")
        for prop in client.list_properties(request=prop_request):
            property_id = prop.name.split("/")[-1]

            stream_request = ListDataStreamsRequest(parent=prop.name)
            for stream in client.list_data_streams(request=stream_request):
                if stream.web_stream_data and stream.web_stream_data.default_uri:
                    domain = _domain(stream.web_stream_data.default_uri)
                    domain_to_property_id[domain] = property_id

    return domain_to_property_id


def _write_property_id(site_id: str, property_id: str) -> bool:
    """
    Replace ga4_property_id for one site's block in config/sites.py,
    matching only within that site's dict (anchored on its quoted
    site_id key) so sites sharing similar values never cross-write.

    @return bool  True if a replacement was made
    """
    text = SITES_FILE.read_text(encoding="utf-8")

    pattern = re.compile(
        rf'("{site_id}":\s*\{{[^}}]*?"ga4_property_id":\s*)(None|\d+)(,)',
        re.DOTALL,
    )
    new_text, count = pattern.subn(rf"\g<1>{property_id}\g<3>", text)

    if count == 0:
        return False

    SITES_FILE.write_text(new_text, encoding="utf-8")
    return True


def main():
    creds = get_credentials()
    client = AnalyticsAdminServiceClient(credentials=creds)

    print("Discovering GA4 properties and matching to sites by domain...\n")
    domain_to_property_id = _discover_properties(client)

    matched = []
    unmatched = []

    for site_id, config in SITES.items():
        site_domain = _domain(config["gsc_property"])
        property_id = domain_to_property_id.get(site_domain)

        if property_id:
            written = _write_property_id(site_id, property_id)
            matched.append((site_id, config["label"], property_id, written))
        else:
            unmatched.append((site_id, config["label"], site_domain))

    print("Matched and written:")
    for site_id, label, property_id, written in matched:
        status = "written" if written else "MATCH FOUND BUT WRITE FAILED — set manually"
        print(f"  {label} ({site_id}): {property_id}  [{status}]")

    if unmatched:
        print("\nNo GA4 property found for these — check they're added as Viewer:")
        for site_id, label, domain in unmatched:
            print(f"  {label} ({site_id})  — looked for domain: {domain}")

    print(f"\nDone. {len(matched)}/{len(SITES)} sites matched.")


if __name__ == "__main__":
    main()

