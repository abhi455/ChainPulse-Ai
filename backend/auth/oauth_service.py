from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.auth import create_access_token
from backend.auth.oauth_config import (
    OAUTH_DEFAULT_ORGANIZATION_ID,
)
from backend.database.models import (
    OAuthLoginCode,
    User,
    UserIdentity,
)
from backend.database.repositories import (
    UserIdentityRepository,
)


class OAuthIdentityService:

    @staticmethod
    def normalize_profile(
        provider: str,
        profile: dict,
    ) -> dict[str, str | None]:

        provider = provider.lower()

        if provider == "google":
            subject = (
                profile.get("sub")
                or profile.get("id")
            )

            email = profile.get("email")
            name = (
                profile.get("name")
                or profile.get("given_name")
                or email
            )

        elif provider == "microsoft":
            subject = (
                profile.get("sub")
                or profile.get("oid")
                or profile.get("id")
            )

            email = (
                profile.get("email")
                or profile.get("preferred_username")
            )

            name = (
                profile.get("name")
                or email
            )

        elif provider == "meta":
            subject = (
                profile.get("id")
                or profile.get("sub")
            )

            email = profile.get("email")
            name = (
                profile.get("name")
                or email
            )

        else:
            raise ValueError(
                f"Unsupported OAuth provider: {provider}"
            )

        if not subject:
            raise ValueError(
                f"{provider} did not return a stable subject."
            )

        if not email:
            raise ValueError(
                f"{provider} did not return an email address."
            )

        return {
            "provider": provider,
            "provider_subject": str(subject),
            "email": str(email).strip().lower(),
            "name": str(name or "ChainPulse User").strip(),
        }

    @staticmethod
    def get_or_create_user(
        db: Session,
        identity: dict[str, str | None],
    ) -> tuple[User, UserIdentity]:

        provider = str(
            identity["provider"]
        )

        provider_subject = str(
            identity["provider_subject"]
        )

        email = str(
            identity["email"]
        ).lower()

        name = str(
            identity["name"]
        )

        repo = UserIdentityRepository(db)

        existing_identity = (
            repo.get_by_provider_subject(
                provider,
                provider_subject,
            )
        )

        if existing_identity:
            user = db.get(
                User,
                existing_identity.user_id,
            )

            if user is None:
                raise HTTPException(
                    status_code=401,
                    detail="Linked user account not found.",
                )

            existing_identity.last_used_at = (
                datetime.utcnow()
            )

            return user, existing_identity

        user = db.scalar(
            select(User).where(
                User.email == email
            )
        )

        if user is None:

            if not OAUTH_DEFAULT_ORGANIZATION_ID:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        "No ChainPulse account exists for "
                        f"{email}. An administrator must "
                        "provision the account first."
                    ),
                )

            user = User(
                organization_id=(
                    OAUTH_DEFAULT_ORGANIZATION_ID
                ),
                name=name,
                email=email,
                password_hash=None,
                role="user",
                is_active=True,
            )

            db.add(user)
            db.flush()

        identity_record = UserIdentity(
            user_id=user.id,
            provider=provider,
            provider_subject=provider_subject,
            email=email,
            last_used_at=datetime.utcnow(),
        )

        db.add(identity_record)
        db.flush()

        return user, identity_record

    @staticmethod
    def issue_exchange_code(
        db: Session,
        user: User,
    ) -> str:

        raw_code = secrets.token_urlsafe(48)

        code_hash = hashlib.sha256(
            raw_code.encode("utf-8")
        ).hexdigest()

        record = OAuthLoginCode(
            user_id=user.id,
            code_hash=code_hash,
            expires_at=(
                datetime.utcnow()
                + timedelta(minutes=5)
            ),
        )

        db.add(record)
        db.commit()

        return raw_code

    @staticmethod
    def exchange_code(
        db: Session,
        raw_code: str,
    ) -> str:

        code_hash = hashlib.sha256(
            raw_code.encode("utf-8")
        ).hexdigest()

        record = db.scalar(
            select(OAuthLoginCode).where(
                OAuthLoginCode.code_hash
                == code_hash
            )
        )

        if record is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid OAuth exchange code.",
            )

        if record.consumed_at is not None:
            raise HTTPException(
                status_code=401,
                detail="OAuth exchange code already used.",
            )

        if record.expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=401,
                detail="OAuth exchange code expired.",
            )

        user = db.get(
            User,
            record.user_id,
        )

        if user is None or not user.is_active:
            raise HTTPException(
                status_code=401,
                detail="User account is unavailable.",
            )

        record.consumed_at = datetime.utcnow()

        token = create_access_token(
            subject=user.id,
            organization_id=user.organization_id,
        )

        db.commit()

        return token
