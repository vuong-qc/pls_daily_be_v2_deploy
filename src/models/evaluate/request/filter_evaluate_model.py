from typing import Optional
from pydantic import BaseModel, Field

class FilterEvaluateModel(BaseModel):
    assigned_id: Optional[list[str]] = None
    update_user: Optional[list[str]] = None
    creator_id: Optional[list[str]] = None
    value: Optional[int] = None
    point: Optional[int] = None
    offset: int = 0
    limit: int = Field(10, le=100)
    start_time: Optional[int] = None
    end_time: Optional[int] = None