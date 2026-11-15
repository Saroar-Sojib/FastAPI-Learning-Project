# schemas/employee.py
from datetime import date
from pydantic import BaseModel, ConfigDict, Field

from app.enums import UserStatus


class EmployeeBase(BaseModel):
    employee_code: str = Field(min_length=1, max_length=50)
    full_name: str = Field(min_length=1, max_length=150)
    designation: str | None = Field(default=None, max_length=100)
    department: str | None = Field(default=None, max_length=100)
    joining_date: date | None = None


class EmployeeCreate(EmployeeBase):
    user_id: int


class EmployeeUpdate(BaseModel):
    # everything optional, so it works for PATCH; user_id is not updatable
    employee_code: str | None = Field(default=None, min_length=1, max_length=50)
    full_name: str | None = Field(default=None, min_length=1, max_length=150)
    designation: str | None = Field(default=None, max_length=100)
    department: str | None = Field(default=None, max_length=100)
    joining_date: date | None = None

    model_config = ConfigDict(extra="forbid")


class UserBrief(BaseModel):
    id: int
    email: str
    status: UserStatus
    is_verified: bool

    model_config = ConfigDict(from_attributes=True)


class EmployeeResponse(EmployeeBase):
    id: int
    user_id: int
    user: UserBrief | None = None   # nested user; drop this if you don't want it

    model_config = ConfigDict(from_attributes=True)