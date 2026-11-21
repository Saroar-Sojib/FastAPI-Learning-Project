"""
Shared FastAPI dependencies for authentication.

Protect any route by adding:

    current_user: User = Depends(get_current_user)
"""

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.models import User
from app.services import AuthService

# HTTPBearer makes Swagger's "Authorize" button show a single "Value" box.
# Paste the access_token from /auth/login there (without the word "Bearer").
bearer_scheme = HTTPBearer(description="Paste the access_token from /auth/login")


def get_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> str:
    """Reads `Authorization: Bearer <token>` and returns just the token string."""
    return credentials.credentials


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


def get_current_user(
    token: str = Depends(get_token),
    auth: AuthService = Depends(get_auth_service),
) -> User:
    """Validates the access token and returns the logged-in user."""
    return auth.get_current_user(token)
