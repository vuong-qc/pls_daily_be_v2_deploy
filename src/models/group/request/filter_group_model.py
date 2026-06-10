from pydantic import BaseModel, Field
from src.enums.group_type_enum import GroupType
from typing import Optional

class FilterGroupModel(BaseModel):
    type: Optional[list[GroupType]] = None
    search: Optional[str] = None
    offset: int = 0
    limit: int = Field(10, le=100)
    created_by: Optional[str] = None
    parent_type: Optional[str] = None