"""
collectors/gsc_auth.py

Handles OAuth for a single site's Search Console access.

Each site gets its own token file (config/sites.py -> token_path) even
though they may share one Google Cloud OAuth client (credentials.json).
This means revoking or re-authing one site never touches the others.

First run for a site opens a browser consent screen. After that,
the refresh token is reused silently until Google invalidates it.
"""

from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from config.sites import CREDENTIALS_PATH, GSC_SCOPES


def get_credentials(token_path: Path) -> Credentials:
    """
    Return valid Credentials for a site, refreshing or running the
    OAuth consent flow as needed.

    @param token_path  Path  Where this site's token is cached (config/sites.py)
    @return Credentials
    """
    creds = None

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), GSC_SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # NOTE: silent refresh — no browser popup needed.
            creds.refresh(Request())
        else:
            # NOTE: first-time auth for this site. Opens a browser window.
            # Requires config/credentials.json (OAuth client from Google
            # Cloud Console) to exist — see README for setup steps.
            if not CREDENTIALS_PATH.exists():
                raise FileNotFoundError(
                    f"Missing {CREDENTIALS_PATH}. Download your OAuth client "
                    "credentials from Google Cloud Console and save them there."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_PATH), GSC_SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Cache the (possibly refreshed) token for next time.
        token_path.parent.mkdir(parents=True, exist_ok=True)
        token_path.write_text(creds.to_json())

    return creds
