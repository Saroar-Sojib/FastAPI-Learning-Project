
from fastapi import FastAPI
from app.api.first_fast_api_class import router as first_fast_api_app
from app.api.first_fast_api_class_2nd_part import router as first_fast_api_class_2nd_part
# Create the application instance
app = FastAPI(
    title="FastAPI Learning API"
)
app.include_router(first_fast_api_app,prefix="/first_fast_api",tags=["first_fast_api"])
app.include_router(first_fast_api_class_2nd_part,prefix="/first_fast_api_v2",tags=["first_fast_api_v2"])

