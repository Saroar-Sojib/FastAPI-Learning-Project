"""
Root API router.

Every feature router is included here once, and main.py includes only this.
Adding a new feature = one new `include_router` line below.
"""

from fastapi import APIRouter

from app.api.v1.auth_routes import router as auth_router
from app.api.v1.user_routes import router as user_router
from app.api.v1.employee_routes import router as employee_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(user_router, prefix="/users", tags=["Users"])
api_router.include_router(employee_router, prefix="/employees", tags=["Employees"])
