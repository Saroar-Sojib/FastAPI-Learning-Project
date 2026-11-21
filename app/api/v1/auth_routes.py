"""
Auth routes.

  POST /auth/register    create an account (public)
  POST /auth/login       email + password (JSON) -> access + refresh token
  POST /auth/refresh     refresh token -> new access + refresh token
  POST /auth/logout      revoke the current session
  POST /auth/logout-all  revoke every session of the current user
  GET  /auth/me          the logged-in user
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_auth_service, get_current_user, get_token
from app.infrastructure.database import get_db
from app.models import User
from app.schemas import (
    LoginRequest,
    MessageResponse,
    RefreshRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
)
from app.services import AuthService, UserService

router = APIRouter()


# @router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
# def register(payload: UserCreate, db: Session = Depends(get_db)):
#     return UserService(db).create_user(payload)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, auth: AuthService = Depends(get_auth_service)):
    return auth.login(email=payload.email, password=payload.password)


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, auth: AuthService = Depends(get_auth_service)):
    return auth.refresh(payload.refresh_token)


@router.post("/logout", response_model=MessageResponse)
def logout(
    token: str = Depends(get_token),
    auth: AuthService = Depends(get_auth_service),
):
    auth.logout(token)
    return MessageResponse(detail="Logged out")


@router.post("/logout-all", response_model=MessageResponse)
def logout_all(
    current_user: User = Depends(get_current_user),
    auth: AuthService = Depends(get_auth_service),
):
    auth.logout_all(current_user)
    return MessageResponse(detail="Logged out from all devices")


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user
