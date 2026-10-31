"""
User service.

The service layer holds business rules (e.g. "email must be unique",
"hash the password before saving"). It uses the repository for DB access
and raises HTTPException so routes stay thin.
"""

import hashlib

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import User
from app.repositories import UserRepository
from app.schemas import UserCreate, UserUpdate


def hash_password(raw_password: str) -> str:
    # NOTE: for learning only. Real projects use bcrypt / argon2 (e.g. passlib).
    return hashlib.sha256(raw_password.encode()).hexdigest()


class UserService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def list_users(self, skip: int = 0, limit: int = 20) -> list[User]:
        return self.repo.get_all(skip=skip, limit=limit)

    def get_user(self, user_id: int) -> User:
        user = self.repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    def create_user(self, data: UserCreate) -> User:
        if self.repo.get_by_email(data.email) is not None:
            raise HTTPException(status.HTTP_409_CONFLICT, detail="Email already registered")

        user = User(
            full_name=data.full_name,
            email=data.email,
            hashed_password=hash_password(data.password),
            role=data.role,
        )
        return self.repo.create(user)

    def update_user(self, user_id: int, data: UserUpdate) -> User:
        user = self.get_user(user_id)

        # exclude_unset -> only the fields the client actually sent
        changes = data.model_dump(exclude_unset=True)

        new_email = changes.get("email")
        if new_email and new_email != user.email and self.repo.get_by_email(new_email):
            raise HTTPException(status.HTTP_409_CONFLICT, detail="Email already registered")

        return self.repo.update(user, changes)

    def delete_user(self, user_id: int) -> None:
        user = self.get_user(user_id)
        self.repo.delete(user)
