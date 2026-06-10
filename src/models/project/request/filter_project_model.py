from typing import Optional

from pydantic import BaseModel, Field

class FilterProjectModel(BaseModel):
    group_id: Optional[str] = None
    handler_id: Optional[list[str]] = None
    search: Optional[str] = None
    offset: int =0
    limit: int = Field(10, le=100)