"""
Pydantic schemas for the User resource.

Schemas define what the API accepts (request body) and returns (response body).
They are separate from the ORM model so the DB shape and API shape can differ
(e.g. we never return `hashed_password`).
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.enums import UserRole, UserStatus


class UserBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100, examples=["Saroar Sojib"])
    email: EmailStr = Field(..., examples=["sojib@example.com"])


class UserCreate(UserBase):
    """Body for POST /users"""

    password: str = Field(..., min_length=6, max_length=72, examples=["secret123"])
    role: UserRole = UserRole.USER


class UserUpdate(BaseModel):
    """Body for PATCH /users/{id}. Every field is optional."""

    full_name: str | None = Field(None, min_length=2, max_length=100)
    email: EmailStr | None = None
    role: UserRole | None = None
    status: UserStatus | None = None
    is_verified: bool | None = None


class UserResponse(UserBase):
    """What the API returns. Never includes the password."""

    id: int
    role: UserRole
    status: UserStatus
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    # Allows building this schema directly from an ORM object:
    #   UserResponse.model_validate(user_orm_obj)
    model_config = ConfigDict(from_attributes=True)
