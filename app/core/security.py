"""
Security helpers: password hashing + JWT creation/decoding.

This module knows nothing about the database or HTTP. It only does crypto.

Two kinds of JWT are issued:
  - access token  : short-lived (minutes). Sent on every request as
                    `Authorization: Bearer <token>`.
  - refresh token : long-lived (days). Used ONLY at /auth/refresh to get a
                    new access token when the old one expires.

Both tokens carry a `sid` (session id). The session row lives in the
`refresh_tokens` table. Logout revokes that row, which instantly kills
both the refresh token and every access token issued with the same sid.
"""

import hashlib
import hmac
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt

from app.core.config import settings

ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


# ---------- Passwords ----------

def hash_password(raw_password: str) -> str:
    """Hash a password with bcrypt (salted, slow on purpose)."""
    return bcrypt.hashpw(raw_password.encode(), bcrypt.gensalt()).decode()


def verify_password(raw_password: str, hashed_password: str) -> bool:
    """
    Check a password against its stored hash.

    Users created before bcrypt was added have a plain SHA-256 hex hash.
    We still accept those so old accounts can log in (AuthService then
    upgrades them to bcrypt on successful login).
    """
    if is_legacy_hash(hashed_password):
        legacy = hashlib.sha256(raw_password.encode()).hexdigest()
        return hmac.compare_digest(legacy, hashed_password)
    try:
        return bcrypt.checkpw(raw_password.encode(), hashed_password.encode())
    except ValueError:
        return False


def is_legacy_hash(hashed_password: str) -> bool:
    return not hashed_password.startswith("$2")


# ---------- JWT ----------

def _create_token(
    user_id: int, token_type: str, session_id: str, expires_delta: timedelta
) -> tuple[str, datetime]:
    now = datetime.now(timezone.utc)
    expires_at = now + expires_delta
    payload: dict[str, Any] = {
        "sub": str(user_id),  # subject = who the token belongs to (must be a string)
        "type": token_type,  # "access" or "refresh"
        "sid": session_id,  # session id -> row in refresh_tokens table
        "jti": uuid.uuid4().hex,  # unique id of this specific token
        "iat": now,  # issued at
        "exp": expires_at,  # expiry (PyJWT checks this automatically on decode)
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, expires_at


def create_access_token(user_id: int, session_id: str) -> str:
    token, _ = _create_token(
        user_id,
        ACCESS_TOKEN_TYPE,
        session_id,
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return token


def create_refresh_token(user_id: int, session_id: str) -> tuple[str, datetime]:
    """Returns (token, expires_at) — expires_at is stored in the DB row."""
    return _create_token(
        user_id,
        REFRESH_TOKEN_TYPE,
        session_id,
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str) -> dict[str, Any]:
    """
    Verify signature + expiry and return the payload.
    Raises jwt.InvalidTokenError (or a subclass like ExpiredSignatureError)
    if anything is wrong.
    """
    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
        options={"require": ["sub", "type", "sid", "exp"]},
    )
