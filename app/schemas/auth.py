"""
Pydantic schemas for authentication.
"""

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., examples=["sojib@example.com"])
    password: str = Field(..., examples=["secret123"])


class TokenResponse(BaseModel):
    """
    Returned by /auth/login and /auth/refresh.

    Copy `access_token` into Swagger's "Authorize" box.
    """

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # access token lifetime in seconds


class RefreshRequest(BaseModel):
    refresh_token: str


class MessageResponse(BaseModel):
    detail: str
