from __future__ import annotations

from authlib.integrations.starlette_client import OAuth

from backend.auth.oauth_config import (
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    META_CLIENT_ID,
    META_CLIENT_SECRET,
    META_GRAPH_API_BASE,
    MICROSOFT_CLIENT_ID,
    MICROSOFT_CLIENT_SECRET,
    MICROSOFT_TENANT,
)

oauth = OAuth()


def configure_oauth() -> None:

    if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
        oauth.register(
            name="google",
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            server_metadata_url=(
                "https://accounts.google.com/"
                ".well-known/openid-configuration"
            ),
            client_kwargs={
                "scope": "openid email profile",
            },
        )

    if MICROSOFT_CLIENT_ID and MICROSOFT_CLIENT_SECRET:
        oauth.register(
            name="microsoft",
            client_id=MICROSOFT_CLIENT_ID,
            client_secret=MICROSOFT_CLIENT_SECRET,
            server_metadata_url=(
                f"https://login.microsoftonline.com/"
                f"{MICROSOFT_TENANT}/v2.0/"
                ".well-known/openid-configuration"
            ),
            client_kwargs={
                "scope": "openid profile email",
            },
        )

    if META_CLIENT_ID and META_CLIENT_SECRET:
        oauth.register(
            name="meta",
            client_id=META_CLIENT_ID,
            client_secret=META_CLIENT_SECRET,
            authorize_url=(
                f"{META_GRAPH_API_BASE}/oauth/authorize"
            ),
            access_token_url=(
                f"{META_GRAPH_API_BASE}/oauth/access_token"
            ),
            client_kwargs={
                "scope": "email,public_profile",
            },
        )


configure_oauth()
