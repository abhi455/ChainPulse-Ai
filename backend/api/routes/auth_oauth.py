from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
)
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from backend.api.dependencies import get_db
from backend.auth.oauth import oauth
from backend.auth.oauth_config import (
    OAUTH_FRONTEND_URL,
    OAUTH_REDIRECT_BASE_URL,
)
from backend.auth.oauth_service import (
    OAuthIdentityService,
)


router = APIRouter(
    prefix="/auth/oauth",
    tags=["Authentication"],
)


SUPPORTED_PROVIDERS = {
    "google",
    "microsoft",
    "meta",
}


def _get_client(provider: str):
    provider = provider.lower()

    if provider not in SUPPORTED_PROVIDERS:
        raise HTTPException(
            status_code=404,
            detail="Unsupported OAuth provider.",
        )

    client = oauth.create_client(provider)

    if client is None:
        raise HTTPException(
            status_code=503,
            detail=(
                f"{provider.title()} OAuth is not configured."
            ),
        )

    return client


@router.get("/{provider}/login")
async def oauth_login(
    provider: str,
    request: Request,
):

    client = _get_client(provider)

    redirect_uri = (
        f"{OAUTH_REDIRECT_BASE_URL}"
        f"/api/v1/auth/oauth/{provider}/callback"
    )

    return await client.authorize_redirect(
        request,
        redirect_uri,
    )


@router.get(
    "/{provider}/callback",
    name="oauth_callback",
)
async def oauth_callback(
    provider: str,
    request: Request,
    db: Session = Depends(get_db),
):

    client = _get_client(provider)

    try:
        token = await client.authorize_access_token(
            request
        )

        profile = {}

        if provider in {
            "google",
            "microsoft",
        }:
            try:
                profile = dict(
                    await client.userinfo(
                        token=token
                    )
                )
            except Exception:
                profile = dict(
                    token.get("userinfo")
                    or {}
                )

        elif provider == "meta":
            userinfo = await client.get(
                f"{client.api_base_url}/me",
                token=token,
                params={
                    "fields":
                        "id,name,email,picture"
                },
            )

            userinfo.raise_for_status()
            profile = userinfo.json()

        identity = (
            OAuthIdentityService.normalize_profile(
                provider,
                profile,
            )
        )

        user, _identity = (
            OAuthIdentityService.get_or_create_user(
                db,
                identity,
            )
        )

        raw_code = (
            OAuthIdentityService.issue_exchange_code(
                db,
                user,
            )
        )

        return RedirectResponse(
            url=(
                f"{OAUTH_FRONTEND_URL}"
                f"?oauth_code={raw_code}"
            )
        )

    except HTTPException:
        raise

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=(
                "OAuth authentication failed: "
                f"{exc}"
            ),
        ) from exc


@router.post("/exchange")
def exchange_oauth_code(
    oauth_code: str,
    db: Session = Depends(get_db),
):
    token = OAuthIdentityService.exchange_code(
        db,
        oauth_code,
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }
