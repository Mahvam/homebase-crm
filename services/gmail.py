"""
services/gmail.py — Gmail OAuth + send
======================================
Lets Danielle connect her own Gmail account and send generated follow-up
emails directly from the app (no copy/paste).

Setup (one time, in Google Cloud Console):
  1. Create a project, enable the "Gmail API".
  2. Configure the OAuth consent screen (External; add your Google account as a
     test user while in "Testing" mode).
  3. Create an OAuth 2.0 Client ID of type "Web application".
  4. Add this Authorized redirect URI:
        http://localhost:8000/admin/gmail/callback
     (and your production URL's /admin/gmail/callback when you deploy).
  5. Put the client ID + secret in your .env:
        GMAIL_CLIENT_ID=...
        GMAIL_CLIENT_SECRET=...

Scope is gmail.send only (least privilege) plus openid/email so we can show
which account is connected. The refresh token is stored in the DB (Setting),
so the connection survives restarts.

All Google library imports are lazy so the rest of the app still boots if the
packages aren't installed yet.
"""

import os

# Allow the OAuth callback over plain http on localhost during development.
os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")
# Google may grant openid/email in a different order than requested.
os.environ.setdefault("OAUTHLIB_RELAX_TOKEN_SCOPE", "1")

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/gmail.send",
]
AUTH_URI = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URI = "https://oauth2.googleapis.com/token"


def _client_id():
    return os.getenv("GMAIL_CLIENT_ID", "")


def _client_secret():
    return os.getenv("GMAIL_CLIENT_SECRET", "")


def is_configured():
    """True once the OAuth client credentials are present."""
    return bool(_client_id() and _client_secret())


def is_connected():
    """True once a Gmail account has been authorized (refresh token stored)."""
    try:
        from models import Setting
        return bool(Setting.get("GMAIL_REFRESH_TOKEN"))
    except Exception:
        return False


def connected_email():
    try:
        from models import Setting
        return Setting.get("GMAIL_CONNECTED_EMAIL") or ""
    except Exception:
        return ""


def _client_config(redirect_uri):
    return {
        "web": {
            "client_id": _client_id(),
            "client_secret": _client_secret(),
            "auth_uri": AUTH_URI,
            "token_uri": TOKEN_URI,
            "redirect_uris": [redirect_uri],
        }
    }


def get_auth_url(redirect_uri, state=None):
    """Build the Google consent URL. Returns (url, state)."""
    from google_auth_oauthlib.flow import Flow
    flow = Flow.from_client_config(_client_config(redirect_uri), scopes=SCOPES, redirect_uri=redirect_uri)
    url, state = flow.authorization_url(
        access_type="offline",         # we want a refresh token
        prompt="consent",              # force a refresh token even on re-connect
        include_granted_scopes="true",
        state=state,
    )
    return url, state


def exchange_code(redirect_uri, code, state=None):
    """Exchange the auth code for tokens, store the refresh token + email.

    Returns the connected email address (best effort)."""
    from models import Setting
    from google_auth_oauthlib.flow import Flow
    flow = Flow.from_client_config(_client_config(redirect_uri), scopes=SCOPES,
                                   redirect_uri=redirect_uri, state=state)
    flow.fetch_token(code=code)
    creds = flow.credentials

    if not creds.refresh_token:
        # Happens if the user previously consented and Google skipped re-issuing
        # a refresh token. prompt="consent" above avoids this, but guard anyway.
        raise RuntimeError("Google did not return a refresh token. Disconnect and try connecting again.")

    Setting.set("GMAIL_REFRESH_TOKEN", creds.refresh_token)

    email = _fetch_email(creds.token)
    if email:
        Setting.set("GMAIL_CONNECTED_EMAIL", email)
    return email


def _fetch_email(access_token):
    import requests
    try:
        r = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
        if r.ok:
            return r.json().get("email", "")
    except Exception:
        pass
    return ""


def disconnect():
    from models import Setting
    Setting.set("GMAIL_REFRESH_TOKEN", "")
    Setting.set("GMAIL_CONNECTED_EMAIL", "")


def send_email(to, subject, body_text):
    """Send a plain-text email from the connected Gmail account.

    Returns the Gmail message id. Raises if Gmail isn't connected."""
    from models import Setting
    if not is_connected():
        raise RuntimeError("Gmail is not connected")

    import base64
    from email.mime.text import MIMEText
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    creds = Credentials(
        token=None,
        refresh_token=Setting.get("GMAIL_REFRESH_TOKEN"),
        client_id=_client_id(),
        client_secret=_client_secret(),
        token_uri=TOKEN_URI,
        scopes=SCOPES,
    )
    service = build("gmail", "v1", credentials=creds, cache_discovery=False)

    msg = MIMEText(body_text)
    msg["to"] = to
    msg["subject"] = subject
    sender = connected_email()
    if sender:
        msg["from"] = sender

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    sent = service.users().messages().send(userId="me", body={"raw": raw}).execute()
    return sent.get("id")
