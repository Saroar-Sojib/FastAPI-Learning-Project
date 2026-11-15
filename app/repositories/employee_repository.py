from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Employee


class EmployeeRepository:
    def __init__(self, db: Session):
        self.db = db

    # ---------- READ ----------

    def get_by_id(self, user_id: int) -> Employee | None:
        # Primary-key lookup. Equivalent to: SELECT * FROM users WHERE id = :id
        res = self.db.get(Employee, user_id)
        return res

    def get_by_code(self, employee_code: str) -> Employee | None:
        stmt = select(Employee).where(Employee.employee_code == employee_code)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_user_id(self, user_id: int) -> Employee | None:
        stmt = select(Employee).where(Employee.user_id == user_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_all(self, skip: int = 0, limit: int = 20) -> list[Employee]:
        stmt = select(Employee).order_by(Employee.id).offset(skip).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    # ---------- WRITE ----------

    def create(self, employee: Employee) -> Employee:
        self.db.add(employee)  # INSERT is queued
        self.db.commit()  # INSERT is executed and committed
        self.db.refresh(employee)  # reload DB-generated values (id, created_at, ...)
        return employee

    def update(self, employee: Employee, data: dict) -> Employee:
        for field, value in data.items():
            setattr(employee, field, value)  # SQLAlchemy tracks changed attributes
        self.db.commit()  # UPDATE is executed
        self.db.refresh(employee)
        return employee

    def delete(self, employee: Employee) -> None:
        self.db.delete(employee)
        self.db.commit()
