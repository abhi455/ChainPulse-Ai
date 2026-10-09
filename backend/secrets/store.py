from __future__ import annotations

import base64
import hashlib
import os


class SecretStore:
    """
    Development-safe secret wrapper.

    Production should replace this with a real
    KMS / Vault / cloud secret manager.
    """

    @staticmethod
    def _key() -> bytes:
        raw = os.getenv(
            "CHAINPULSE_SECRET_KEY",
            "change-this-secret-key-in-production",
        ).encode()

        return hashlib.sha256(raw).digest()

    @classmethod
    def encrypt(cls, value: str) -> str:
        if value is None:
            return ""

        key = cls._key()

        encoded = value.encode()

        encrypted = bytes(
            byte ^ key[i % len(key)]
            for i, byte in enumerate(encoded)
        )

        return base64.urlsafe_b64encode(
            encrypted
        ).decode()

    @classmethod
    def decrypt(cls, value: str) -> str:
        if not value:
            return ""

        key = cls._key()

        encrypted = base64.urlsafe_b64decode(
            value.encode()
        )

        decrypted = bytes(
            byte ^ key[i % len(key)]
            for i, byte in enumerate(encrypted)
        )

        return decrypted.decode()
