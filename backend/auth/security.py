from datetime import datetime, timezone

import bcrypt
from jose import JWTError, jwt

from backend.auth.config import (
    JWT_ACCESS_TOKEN_EXPIRE,
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
)


def hash_password(password: str) -> str:
    if not password:
        raise ValueError("Password cannot be empty")

    password_bytes = password.encode("utf-8")

    if len(password_bytes) > 72:
        raise ValueError(
            "Password cannot exceed 72 bytes"
        )

    return bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt(),
    ).decode("utf-8")


def verify_password(
    plain_password: str,
    password_hash: str,
) -> bool:
    if not plain_password or not password_hash:
        return False

    password_bytes = plain_password.encode("utf-8")

    if len(password_bytes) > 72:
        return False

    try:
        return bcrypt.checkpw(
            password_bytes,
            password_hash.encode("utf-8"),
        )
    except (ValueError, TypeError):
        return False


def create_access_token(
    subject: str,
    organization_id: str | None = None,
) -> str:

    if not subject:
        raise ValueError(
            "Token subject cannot be empty"
        )

    now = datetime.now(timezone.utc)

    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + JWT_ACCESS_TOKEN_EXPIRE,
    }

    if organization_id is not None:
        payload["organization_id"] = organization_id

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> dict:
    if not token:
        raise ValueError(
            "Token cannot be empty"
        )

    try:
        return jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )
    except JWTError as exc:
        raise ValueError(
            "Invalid or expired access token"
        ) from exc
