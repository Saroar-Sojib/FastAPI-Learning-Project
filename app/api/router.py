"""
Root API router.

Every feature router is included here once, and main.py includes only this.
Adding a new feature = one new `include_router` line below.
"""

from fastapi import APIRouter

from app.api.v1.user_routes import router as user_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(user_router, prefix="/users", tags=["Users"])
