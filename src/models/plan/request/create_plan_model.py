from pydantic import BaseModel
from typing import Optional

class CreatePlanModel(BaseModel):
    user_id: str
    to_do: Optional[list[str]] = None
    note: Optional[str] = None
    task: Optional[list[str]] = None
    date: int