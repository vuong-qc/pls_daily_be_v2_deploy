from typing import Optional

from pydantic import BaseModel, Field
from src.enums.tag_status_enum import TagStatusEnum

class FilterTagModel(BaseModel):
    status: int = Field(default=TagStatusEnum.ENABLE,le=TagStatusEnum.ENABLE.value,gt=TagStatusEnum.DISABLED.value)
    limit: int = Field(default=10,le=100)
    offset: int = Field(default=0)
    group_id: Optional[list[str]] = None
    tags: Optional[list[str]] = None
    search: Optional[str] = None