"""Security utilities: AES-256 encryption, audit logging (NFR-08..NFR-10)."""

import hashlib
import logging
from datetime import datetime, timezone

from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


def derive_fernet_key(secret: str) -> bytes:
    """Derive a Fernet-compatible key from application secret."""
    digest = hashlib.sha256(secret.encode()).digest()
    import base64

    return base64.urlsafe_b64encode(digest)


class DataEncryptor:
    """AES-256 encryption for data at rest (NFR-09)."""

    def __init__(self, key: str):
        self._fernet = Fernet(derive_fernet_key(key))

    def encrypt(self, data: bytes) -> bytes:
        return self._fernet.encrypt(data)

    def decrypt(self, token: bytes) -> bytes:
        return self._fernet.decrypt(token)


def audit_log(action: str, user: str = "system", details: str = "") -> None:
    """Log access and configuration changes (NFR-10)."""
    logger.info(
        "AUDIT | time=%s user=%s action=%s details=%s",
        datetime.now(timezone.utc).isoformat(),
        user,
        action,
        details,
    )
