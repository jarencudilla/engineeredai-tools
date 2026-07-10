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
TOKENS_DIR = BASE_DIR / "config" / "tokens"

# NOTE: gsc_property must exactly match the property as it appears
# in Google Search Console (usually "https://example.com/" with
# trailing slash, or "sc-domain:example.com" for domain properties).
SITES = {
    "qaj": {
        "label": "QAJourney",
        "gsc_property": "https://qajourney.net/",
        "db_path": DATA_DIR / "qaj.db",
        "token_path": TOKENS_DIR / "qaj_token.json",
    },
    "eai": {
        "label": "EngineeredAI",
        "gsc_property": "https://engineeredai.net/",
        "db_path": DATA_DIR / "eai.db",
        "token_path": TOKENS_DIR / "eai_token.json",
    },
    "mmp": {
        "label": "MomentumPath",
        "gsc_property": "https://momentumpath.net/",
        "db_path": DATA_DIR / "mmp.db",
        "token_path": TOKENS_DIR / "mmp_token.json",
    },
    "hf": {
        "label": "HealthyForge",
        "gsc_property": "https://healthyforge.com/",
        "db_path": DATA_DIR / "hf.db",
        "token_path": TOKENS_DIR / "hf_token.json",
    },
    "rwh": {
        "label": "RemoteWorkHaven",
        "gsc_property": "https://remoteworkhaven.net/",
        "db_path": DATA_DIR / "rwh.db",
        "token_path": TOKENS_DIR / "rwh_token.json",
    },
    "he": {
        "label": "HobbyEngineered",
        "gsc_property": "https://hobbyengineered.com/",
        "db_path": DATA_DIR / "he.db",
        "token_path": TOKENS_DIR / "he_token.json",
    },
}

# Shared OAuth client credentials (one Google Cloud project, one
# credentials.json, used to auth against all six site tokens).
CREDENTIALS_PATH = BASE_DIR / "config" / "credentials.json"

GSC_SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]


def get_site(site_id: str) -> dict:
    """
    Look up a site's config by its short id (e.g. "qaj").
    Raises KeyError with a clear message if the site isn't registered.
    """
    if site_id not in SITES:
        raise KeyError(f"Unknown site_id '{site_id}'. Registered sites: {list(SITES.keys())}")
    return SITES[site_id]
