from typing import Optional
from pydantic import BaseModel, Field


class FilterDepartmentModel(BaseModel):
    list_ids: Optional[list[str]] = None
    limit: int = Field(10, le=100)
    offset: int = 0