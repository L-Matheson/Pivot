"""Fernet-based encryption for connection credentials."""

import base64
import hashlib
import json
from typing import Any

from cryptography.fernet import Fernet


def _derive_key(secret: str) -> bytes:
    digest = hashlib.sha256(secret.encode()).digest()
    return base64.urlsafe_b64encode(digest)


def encrypt_credentials(data: dict[str, Any], key: str) -> bytes:
    fernet = Fernet(_derive_key(key))
    return fernet.encrypt(json.dumps(data).encode())


def decrypt_credentials(token: bytes, key: str) -> dict[str, Any]:
    fernet = Fernet(_derive_key(key))
    return json.loads(fernet.decrypt(token).decode())
