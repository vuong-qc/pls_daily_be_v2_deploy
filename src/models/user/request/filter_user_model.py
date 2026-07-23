from pydantic import BaseModel, Field
from typing import Optional

class FilterUserModel(BaseModel):
    offset: int = 0
    limit: int = Field(10,le=100)
    keyword: Optional[str] = None
    roles: Optional[list[int]] = None
    status: Optional[int] = None
    department: Optional[list[str]] = None