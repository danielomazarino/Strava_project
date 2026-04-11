from __future__ import annotations

import hashlib
import hmac
import secrets
from base64 import urlsafe_b64decode
from base64 import urlsafe_b64encode
from datetime import datetime, timezone

from cryptography.fernet import Fernet

from app.core.config import get_settings

TOKEN_ENCRYPTION_VERSION = 1
OAUTH_STATE_TTL_SECONDS = 300


def _resolve_secret_key(secret_key: str | None = None) -> str:
    resolved_secret_key = secret_key or get_settings().secret_key
    if not resolved_secret_key:
        raise RuntimeError("SECRET_KEY is not configured")
    return resolved_secret_key


def _derive_fernet_key(secret_key: str) -> bytes:
    digest = hashlib.sha256(secret_key.encode("utf-8")).digest()
    return urlsafe_b64encode(digest)


def encrypt_secret(value: str, secret_key: str | None = None) -> str:
    resolved_secret_key = _resolve_secret_key(secret_key)
    cipher = Fernet(_derive_fernet_key(resolved_secret_key))
    return cipher.encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_secret(token: str, secret_key: str | None = None) -> str:
    resolved_secret_key = _resolve_secret_key(secret_key)
    cipher = Fernet(_derive_fernet_key(resolved_secret_key))
    return cipher.decrypt(token.encode("utf-8")).decode("utf-8")


def _encode_state_return_to(return_to: str) -> str:
    if not return_to:
        return ""

    return urlsafe_b64encode(return_to.encode("utf-8")).decode("utf-8")


def _decode_state_return_to(encoded_return_to: str) -> str:
    if not encoded_return_to:
        return ""

    padding = "=" * (-len(encoded_return_to) % 4)
    return urlsafe_b64decode(f"{encoded_return_to}{padding}").decode("utf-8")


def create_oauth_state(secret_key: str | None = None, *, return_to: str = "") -> str:
    resolved_secret_key = _resolve_secret_key(secret_key)
    issued_at = int(datetime.now(timezone.utc).timestamp())
    nonce = secrets.token_urlsafe(32)
    encoded_return_to = _encode_state_return_to(return_to)
    payload = f"{issued_at}:{nonce}:{encoded_return_to}" if encoded_return_to else f"{issued_at}:{nonce}"
    signature = hmac.new(
        resolved_secret_key.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"{payload}:{signature}"


def unpack_oauth_state(
    state: str,
    secret_key: str | None = None,
    max_age_seconds: int = OAUTH_STATE_TTL_SECONDS,
) -> str | None:
    try:
        issued_at_raw, nonce, encoded_return_to, signature = state.split(":", 3)
    except ValueError:
        try:
            issued_at_raw, nonce, signature = state.split(":", 2)
            encoded_return_to = ""
        except ValueError:
            return None

    try:
        issued_at = int(issued_at_raw)
    except ValueError:
        return None

    resolved_secret_key = _resolve_secret_key(secret_key)
    payload = f"{issued_at}:{nonce}:{encoded_return_to}" if encoded_return_to else f"{issued_at}:{nonce}"
    expected_signature = hmac.new(
        resolved_secret_key.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(signature, expected_signature):
        return None

    current_time = int(datetime.now(timezone.utc).timestamp())
    if not 0 <= current_time - issued_at <= max_age_seconds:
        return None

    return _decode_state_return_to(encoded_return_to)


def verify_oauth_state(
    state: str,
    secret_key: str | None = None,
    max_age_seconds: int = OAUTH_STATE_TTL_SECONDS,
) -> bool:
    return unpack_oauth_state(state, secret_key, max_age_seconds) is not None