from typing import Optional
from pydantic import BaseModel, Field

class FilterTemplateModel(BaseModel):
    status: Optional[list[str]] = None
    search: Optional[str] = None
    created_by: Optional[list[str]] = None
    offset: Optional[int] = None
    type: Optional[str] = None
    limit: Optional[int] = Field(default=None, le=100)
    group: Optional[str] = None