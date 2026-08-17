from pydantic import BaseModel, Field
from typing import Optional

class FilterLogModel(BaseModel):
    user: Optional[list[str]] = None
    text: Optional[str] = None
    type: Optional[list[str]] = None
    position: Optional[list[str]] = None
    object_id: Optional[list[str]] = None
    # created_at: Optional[int] = None
    action: Optional[list[str]] = None
    limit: int = Field(10, lt=100)
    offset: int = 0
    start: Optional[int] = None
    end: Optional[int] = None
    # duration: Optional[int] = None