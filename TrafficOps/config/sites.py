"""
config/sites.py

Registry of all sites TrafficOps knows about.
Each site maps to its own SQLite file and its own GSC property URL.

This is the single source of truth for "what sites exist" —
collectors, database module, and UI all read from this list
instead of hardcoding site names anywhere else.

To add a new site: add one entry here. Nothing else needs to change.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# NOTE: gsc_property must exactly match the property as it appears
# in Google Search Console (usually "https://example.com/" with
# trailing slash, or "sc-domain:example.com" for domain properties).
#
# NOTE: ga4_property_id is the numeric Property ID (NOT the
# Measurement ID that starts with "G-"). Find it in GA4 →
# Admin → Property Settings → Property ID. Fill these in below —
# left as None until you do, so a missing ID fails loudly instead
# of silently querying the wrong property.
SITES = {
    "qaj": {
        "label": "QAJourney",
        "gsc_property": "https://qajourney.net/",
        "ga4_property_id": 470886458,
        "db_path": DATA_DIR / "qaj.db",
    },
    "eai": {
        "label": "EngineeredAI",
        "gsc_property": "https://engineeredai.net/",
        "ga4_property_id": 471246383,
        "db_path": DATA_DIR / "eai.db",
    },
    "mmp": {
        "label": "MomentumPath",
        "gsc_property": "https://momentumpath.net/",
        "ga4_property_id": 470932315,
        "db_path": DATA_DIR / "mmp.db",
    },
    "hf": {
        "label": "HealthyForge",
        "gsc_property": "https://healthyforge.com/",
        "ga4_property_id": 471093853,
        "db_path": DATA_DIR / "hf.db",
    },
    "rwh": {
        "label": "RemoteWorkHaven",
        "gsc_property": "https://remoteworkhaven.net/",
        "ga4_property_id": 471230029,
        "db_path": DATA_DIR / "rwh.db",
    },
    "he": {
        "label": "HobbyEngineered",
        "gsc_property": "https://hobbyengineered.com/",
        "ga4_property_id": 518569530,
        "db_path": DATA_DIR / "he.db",
    },
}

# Service account key — one key authenticates against both GSC and
# GA4, for all six sites. Per-site access is granted per-property in
# each product's own console (Search Console Users, GA4 Property
# Access Management), not by separate credential files.
CREDENTIALS_PATH = BASE_DIR / "config" / "credentials.json"

GSC_SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
GA4_SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]


def get_site(site_id: str) -> dict:
    """
    Look up a site's config by its short id (e.g. "qaj").
    Raises KeyError with a clear message if the site isn't registered.
    """
    if site_id not in SITES:
        raise KeyError(f"Unknown site_id '{site_id}'. Registered sites: {list(SITES.keys())}")
    return SITES[site_id]
