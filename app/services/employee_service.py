
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.models.user import User
from app.repositories.employee_repository import EmployeeRepository
from app.schemas.employee import EmployeeCreate, EmployeeUpdate

class EmployeeService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = EmployeeRepository(db)

    def list_employees(self, skip: int = 0, limit: int = 20) -> list[Employee]:
        return self.repo.get_all(skip=skip, limit=limit)

    def get_employees(self, employee_id: int) -> Employee:
        employee = self.repo.get_by_id(employee_id)
        if employee is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
        return employee

    def create_employee(self, data: EmployeeCreate) -> Employee:
        if self.db.get(User, data.user_id) is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
        if self.repo.get_by_user_id(data.user_id):
            raise HTTPException(
                status.HTTP_409_CONFLICT, detail="This user already has an employee record"
            )
        if self.repo.get_by_code(data.employee_code):
            raise HTTPException(status.HTTP_409_CONFLICT, detail="Employee code already exists")

        user = Employee(
            employee_code = data.employee_code,
            full_name = data.full_name,
            designation = data.designation,
            department = data.department,
            joining_date = data.joining_date,
            user_id = data.user_id
        )
        return self.repo.create(user)

    def update_employee(self, employee_id: int, data: EmployeeUpdate) -> Employee:
        employee = self.get_employees(employee_id)

        # exclude_unset -> only the fields the client actually sent
        changes = data.model_dump(exclude_unset=True)
        return self.repo.update(employee, changes)

    def delete_employee(self, employee_id: int) -> None:
        user = self.get_employees(employee_id)
        self.repo.delete(user)
