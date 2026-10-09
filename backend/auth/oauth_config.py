from __future__ import annotations

import os


OAUTH_ENABLED = os.getenv(
    "CHAINPULSE_OAUTH_ENABLED",
    "false",
).lower() == "true"

OAUTH_REDIRECT_BASE_URL = os.getenv(
    "CHAINPULSE_OAUTH_REDIRECT_BASE_URL",
    "http://127.0.0.1:8000",
).rstrip("/")

OAUTH_FRONTEND_URL = os.getenv(
    "CHAINPULSE_OAUTH_FRONTEND_URL",
    "http://localhost:8501",
).rstrip("/")

OAUTH_DEFAULT_ORGANIZATION_ID = os.getenv(
    "OAUTH_DEFAULT_ORGANIZATION_ID",
)

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv(
    "GOOGLE_CLIENT_SECRET"
)

MICROSOFT_CLIENT_ID = os.getenv(
    "MICROSOFT_CLIENT_ID"
)
MICROSOFT_CLIENT_SECRET = os.getenv(
    "MICROSOFT_CLIENT_SECRET"
)
MICROSOFT_TENANT = os.getenv(
    "MICROSOFT_TENANT",
    "common",
)

META_CLIENT_ID = os.getenv("META_CLIENT_ID")
META_CLIENT_SECRET = os.getenv(
    "META_CLIENT_SECRET"
)

META_GRAPH_API_BASE = os.getenv(
    "META_GRAPH_API_BASE",
    "https://graph.facebook.com",
)
