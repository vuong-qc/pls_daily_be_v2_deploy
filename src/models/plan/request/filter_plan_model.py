from typing import Optional

from pydantic import BaseModel, Field
class FilterPlanModel(BaseModel):
    start_date: Optional[int] = None
    end_date: Optional[int] = None
    user_ids: Optional[list[str]] = None
    offset: int = 0
    limit: int = Field(10, le=100)