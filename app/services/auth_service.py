"""
Auth service — login, refresh, logout, and resolving the current user.

Flow:
  login    : email + password  -> new session row -> access + refresh token
  refresh  : refresh token     -> old session revoked, new session -> new pair
  logout   : access token      -> its session revoked (both tokens die)
  me       : access token      -> User
"""

import uuid
from datetime import datetime, timezone

import jwt
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    is_legacy_hash,
    verify_password,
)
from app.enums import UserStatus
from app.models import RefreshToken, User
from app.repositories import RefreshTokenRepository, UserRepository
from app.schemas import TokenResponse


def _unauthorized(detail: str = "Could not validate credentials") -> HTTPException:
    # The WWW-Authenticate header is part of the OAuth2 Bearer spec.
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


class AuthService:
    def __init__(self, db: Session):
        self.users = UserRepository(db)
        self.sessions = RefreshTokenRepository(db)

    # ---------- public API ----------

    def login(self, email: str, password: str) -> TokenResponse:
        user = self.users.get_by_email(email)
        # Same error for "no such email" and "wrong password" so attackers
        # cannot discover which emails are registered.
        if user is None or not verify_password(password, user.hashed_password):
            raise _unauthorized("Incorrect email or password")
        self._ensure_active(user)

        # Upgrade old SHA-256 hashes to bcrypt the first time they log in.
        if is_legacy_hash(user.hashed_password):
            self.users.update(user, {"hashed_password": hash_password(password)})

        return self._issue_tokens(user)

    def refresh(self, refresh_token: str) -> TokenResponse:
        payload = self._decode(refresh_token, REFRESH_TOKEN_TYPE)
        session = self._get_active_session(payload)
        user = self._get_user(payload)
        self._ensure_active(user)

        # Rotation: this refresh token can never be used again.
        self.sessions.revoke(session)
        return self._issue_tokens(user)

    def logout(self, access_token: str) -> None:
        payload = self._decode(access_token, ACCESS_TOKEN_TYPE)
        session = self._get_active_session(payload)
        self.sessions.revoke(session)

    def logout_all(self, user: User) -> None:
        self.sessions.revoke_all_for_user(user.id)

    def get_current_user(self, access_token: str) -> User:
        payload = self._decode(access_token, ACCESS_TOKEN_TYPE)
        self._get_active_session(payload)  # rejects tokens of logged-out sessions
        user = self._get_user(payload)
        self._ensure_active(user)
        return user

    # ---------- helpers ----------

    def _issue_tokens(self, user: User) -> TokenResponse:
        session_id = uuid.uuid4().hex
        access_token = create_access_token(user.id, session_id)
        refresh_token, expires_at = create_refresh_token(user.id, session_id)

        self.sessions.create(
            RefreshToken(session_id=session_id, user_id=user.id, expires_at=expires_at)
        )
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    def _decode(self, token: str, expected_type: str) -> dict:
        try:
            payload = decode_token(token)
        except jwt.ExpiredSignatureError:
            raise _unauthorized("Token has expired")
        except jwt.InvalidTokenError:
            raise _unauthorized("Invalid token")

        # Stops someone from using a refresh token as an access token (or vice versa).
        if payload.get("type") != expected_type:
            raise _unauthorized(f"Invalid token type, expected '{expected_type}' token")
        return payload

    def _get_active_session(self, payload: dict) -> RefreshToken:
        session = self.sessions.get_by_session_id(payload["sid"])
        if session is None or session.revoked_at is not None:
            raise _unauthorized("Session has been logged out")
        if session.expires_at <= datetime.now(timezone.utc):
            raise _unauthorized("Session has expired")
        return session

    def _get_user(self, payload: dict) -> User:
        try:
            user_id = int(payload["sub"])
        except (TypeError, ValueError):
            raise _unauthorized("Invalid token")
        user = self.users.get_by_id(user_id)
        if user is None:
            raise _unauthorized("User no longer exists")
        return user

    @staticmethod
    def _ensure_active(user: User) -> None:
        if user.status != UserStatus.ACTIVE:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail=f"User is {user.status.value}")
