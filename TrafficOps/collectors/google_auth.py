"""
collectors/google_auth.py

Handles auth for Google APIs using a service account — not OAuth.

trafficops-reader@trafficops.iam.gserviceaccount.com already has
Viewer access added per site in both Search Console and GA4. This
module loads the service account key once and mints credentials
scoped for both APIs, so GSC and GA4 collectors share one function
instead of each managing their own auth.

No browser consent screen, no per-site token cache, no refresh
logic — service account keys don't expire the way OAuth user
tokens do.
"""

from google.oauth2 import service_account

from config.sites import CREDENTIALS_PATH, GSC_SCOPES, GA4_SCOPES

ALL_SCOPES = GSC_SCOPES + GA4_SCOPES


def get_credentials():
    """
    Load service account credentials from config/credentials.json,
    scoped for both Search Console and GA4 access.

    @return service_account.Credentials
    """
    if not CREDENTIALS_PATH.exists():
        raise FileNotFoundError(
            f"Missing {CREDENTIALS_PATH}. Download the JSON key for "
            "trafficops-reader@trafficops.iam.gserviceaccount.com "
            "(Cloud Console → Service Accounts → Keys → Add Key → JSON) "
            "and save it there."
        )

    return service_account.Credentials.from_service_account_file(
        str(CREDENTIALS_PATH), scopes=ALL_SCOPES
    )
