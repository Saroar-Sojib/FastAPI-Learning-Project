"""
User repository.

The repository layer is the ONLY place that talks to the database.
It knows SQLAlchemy; it knows nothing about HTTP or business rules.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    # ---------- READ ----------

    def get_by_id(self, user_id: int) -> User | None:
        # Primary-key lookup. Equivalent to: SELECT * FROM users WHERE id = :id
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_all(self, skip: int = 0, limit: int = 20) -> list[User]:
        stmt = select(User).order_by(User.id).offset(skip).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    # ---------- WRITE ----------

    def create(self, user: User) -> User:
        self.db.add(user)  # INSERT is queued
        self.db.commit()  # INSERT is executed and committed
        self.db.refresh(user)  # reload DB-generated values (id, created_at, ...)
        return user

    def update(self, user: User, data: dict) -> User:
        for field, value in data.items():
            setattr(user, field, value)  # SQLAlchemy tracks changed attributes
        self.db.commit()  # UPDATE is executed
        self.db.refresh(user)
        return user

    def delete(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()
