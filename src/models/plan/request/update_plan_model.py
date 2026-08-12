from typing import Optional
from pydantic import BaseModel
class UpdatePlanModel(BaseModel):
    to_do: Optional[list[str]] = None
    note: Optional[str] = None
    task: Optional[list[str]] = None
    date: Optional[int] = None