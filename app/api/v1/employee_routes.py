from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.schemas.employee import EmployeeCreate, EmployeeResponse, EmployeeUpdate
from app.services.employee_service import EmployeeService

router = APIRouter()


def get_employee_service(db: Session = Depends(get_db)) -> EmployeeService:
    """Dependency: builds a UserService with a request-scoped DB session."""
    return EmployeeService(db)


@router.get("", response_model=list[EmployeeResponse])
def list_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    service: EmployeeService = Depends(get_employee_service),
):
    return service.list_employees(skip=skip, limit=limit)


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(employee_id: int, service: EmployeeService= Depends(get_employee_service)):
    return service.get_employees(employee_id)


@router.post("", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(payload: EmployeeCreate, service: EmployeeService = Depends(get_employee_service)):
    return service.create_employee(payload)


@router.patch("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: int,
    payload: EmployeeUpdate,
    service: EmployeeService = Depends(get_employee_service),
):
    return service.update_employee(employee_id, payload)


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(employee_id: int, service: EmployeeService = Depends(get_employee_service)):
    service.delete_employee(employee_id)
