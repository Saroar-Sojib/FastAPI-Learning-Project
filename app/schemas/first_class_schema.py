from pydantic import BaseModel
from typing import Optional

class CreateData(BaseModel):
    id : int
    name: str

class UpdateData(BaseModel):
    id: int
    name: str

class ResponseData(BaseModel):
    input_id: Optional[int] = None
    name: Optional[str] = None