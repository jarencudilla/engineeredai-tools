"""
collectors/gsc_auth.py

Handles Search Console auth using a service account — not OAuth.

trafficops-reader@trafficops.iam.gserviceaccount.com already has
Viewer access added per site in Search Console. This module just
loads the service account key and mints credentials from it — no
browser consent screen, no per-site token cache, no refresh logic
to maintain, since service account keys don't expire the way OAuth
user tokens do.

One key (config/credentials.json) authenticates against all six
sites, because access is granted per-site inside Search Console,
not per-credential-file.
"""

from google.oauth2 import service_account

from config.sites import CREDENTIALS_PATH, GSC_SCOPES


def get_credentials():
    """
    Load service account credentials from config/credentials.json.

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
        str(CREDENTIALS_PATH), scopes=GSC_SCOPES
    )
